import argparse
import logging
from typing import Any, Dict, List
from rich.console import Console
from rich.table import Table
from rich import box
from argus.engine import ArgusEngine

logger = logging.getLogger(__name__)

PRESET_WATCHLISTS = {
    "mega_tech": ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA"],
    "high_growth": ["PLTR", "SNOW", "CRWD", "DDOG", "NET", "COIN"],
    "semis": ["NVDA", "AMD", "INTC", "TSM", "AVGO", "QCOM", "ASML"],
    "ev_clean": ["TSLA", "RIVN", "LCID", "NIO", "ENPH"]
}

class ArgusScreener:
    """
    Batch quantitative screener for scanning groups of tickers across SEC EDGAR.
    Ranks stocks by forensic risk, accounting anomalies, and default distress.
    """

    def __init__(self):
        self.engine = ArgusEngine()

    def screen_tickers(self, tickers: List[str]) -> List[Dict[str, Any]]:
        results = []
        for t in tickers:
            clean_t = t.strip().upper()
            try:
                report = self.engine.analyze_ticker(clean_t)
                forensics = report.get("forensics", {})
                mkt = report.get("market_data", {})
                beneish = forensics.get("beneish_m_score") or {}
                altman = forensics.get("altman_z_score") or {}
                piotroski = forensics.get("piotroski_f_score") or {}

                results.append({
                    "ticker": clean_t,
                    "name": mkt.get("name", clean_t),
                    "price": mkt.get("current_price", 0.0),
                    "market_cap": mkt.get("market_cap", 0),
                    "risk_score": report.get("risk_score", 0),
                    "beneish_score": beneish.get("score"),
                    "is_manipulator": beneish.get("is_manipulator", False),
                    "altman_score": altman.get("score"),
                    "altman_zone": altman.get("zone", "N/A"),
                    "piotroski_score": piotroski.get("score"),
                    "anomalies_count": len(forensics.get("anomalies", []))
                })
            except Exception as e:
                logger.error(f"Error screening {clean_t}: {e}")

        # Sort descending by risk score (most flagged first)
        results.sort(key=lambda x: x["risk_score"], reverse=True)
        return results

def main():
    parser = argparse.ArgumentParser(description="ARGUS Batch Forensic Screener")
    parser.add_argument("--list", default="mega_tech", choices=list(PRESET_WATCHLISTS.keys()), help="Preset watchlist")
    parser.add_argument("--tickers", nargs="*", help="Custom list of tickers (e.g. NVDA TSLA AAPL)")
    args = parser.parse_args()

    tickers = [t.upper() for t in args.tickers] if args.tickers else PRESET_WATCHLISTS[args.list]

    console = Console(safe_box=True)
    console.print(f"[bold cyan]Running ARGUS Forensic Screener on: {', '.join(tickers)}...[/bold cyan]")

    screener = ArgusScreener()
    results = screener.screen_tickers(tickers)

    table = Table(title="[bold yellow]ARGUS FORENSIC SCREENER LEADERBOARD (SORTED BY RISK)[/bold yellow]", box=box.ROUNDED, expand=True)
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Ticker", style="bold white", width=10)
    table.add_column("Company", width=22)
    table.add_column("Risk Score", justify="center", width=12)
    table.add_column("Beneish M", justify="center", width=12)
    table.add_column("Altman Z", justify="center", width=12)
    table.add_column("Piotroski", justify="center", width=10)
    table.add_column("Anomalies", justify="center", width=10)

    for i, r in enumerate(results, 1):
        risk = r["risk_score"]
        risk_color = "red" if risk >= 60 else ("yellow" if risk >= 30 else "green")
        b_color = "red" if r["is_manipulator"] else "green"

        table.add_row(
            str(i),
            r["ticker"],
            r["name"][:20],
            f"[{risk_color}]{risk}/100[/{risk_color}]",
            f"[{b_color}]{r['beneish_score']}[/{b_color}]",
            str(r["altman_score"]),
            f"{r['piotroski_score']}/9",
            f"[red]{r['anomalies_count']}[/red]" if r['anomalies_count'] > 0 else "[green]0[/green]"
        )

    console.print(table)

if __name__ == "__main__":
    main()
