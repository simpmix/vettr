import argparse
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from argus.engine import ArgusEngine

console = Console(safe_box=True)

def print_cli_report(data: dict):
    ticker = data.get("ticker", "UNKNOWN")
    mkt = data.get("market_data", {})
    forensics = data.get("forensics", {})
    risk_score = data.get("risk_score", 0)

    # 1. Header Banner
    price_str = f"${mkt.get('current_price', 0):,.2f}"
    chg = mkt.get('change_pct', 0)
    chg_color = "green" if chg >= 0 else "red"
    chg_str = f"[{chg_color}]{chg:+.2f}%[/{chg_color}]"

    header_text = Text()
    header_text.append(f"ARGUS TERMINAL // {ticker} : {mkt.get('name', '')}\n", style="bold cyan")
    header_text.append(f"Price: {price_str} ({chg:+.2f}%) | Market Cap: ${mkt.get('market_cap', 0):,}\n", style="white")
    header_text.append(f"Sector: {mkt.get('sector')} | Industry: {mkt.get('industry')}", style="dim")

    risk_style = "bold green" if risk_score < 30 else ("bold yellow" if risk_score < 60 else "bold red")
    console.print(Panel(header_text, title=f"[{risk_style}] COMPOSITE RISK SCORE: {risk_score}/100 [/{risk_style}]", border_style="cyan"))

    # 2. Forensic Scorecard Table
    score_table = Table(title="[bold yellow]QUANTITATIVE FORENSIC METRICS[/bold yellow]", box=box.ROUNDED, expand=True)
    score_table.add_column("Model", style="bold white", width=22)
    score_table.add_column("Score", style="cyan", width=12)
    score_table.add_column("Benchmark Threshold", style="dim", width=20)
    score_table.add_column("Forensic Assessment", style="magenta")

    # Beneish
    b = forensics.get("beneish_m_score")
    if b:
        b_color = "red" if b.get("is_manipulator") else "green"
        score_table.add_row(
            "Beneish M-Score",
            f"[{b_color}]{b.get('score')}[/{b_color}]",
            "Threshold: -1.78",
            f"[{b_color}]{b.get('status')}[/{b_color}]"
        )

    # Altman Z
    z = forensics.get("altman_z_score")
    if z:
        z_color = "green" if z.get("risk_level") == "low" else ("yellow" if z.get("risk_level") == "medium" else "red")
        score_table.add_row(
            "Altman Z-Score",
            f"[{z_color}]{z.get('score')}[/{z_color}]",
            "Safe > 2.99, Distress < 1.81",
            f"[{z_color}]{z.get('zone')}[/{z_color}]"
        )

    # Piotroski F
    f = forensics.get("piotroski_f_score")
    if f:
        f_color = "green" if f.get("score", 0) >= 7 else ("yellow" if f.get("score", 0) >= 5 else "red")
        score_table.add_row(
            "Piotroski F-Score",
            f"[{f_color}]{f.get('score')} / 9[/{f_color}]",
            "High: 8-9, Low: 0-4",
            f"[{f_color}]{f.get('rating')}[/{f_color}]"
        )

    console.print(score_table)

    # 3. Anomaly Flags
    anomalies = forensics.get("anomalies", [])
    if anomalies:
        ano_table = Table(title="[bold red]DETECTED FINANCIAL ANOMALIES & DIVERGENCES[/bold red]", box=box.ROUNDED, expand=True)
        ano_table.add_column("Severity", style="bold red", width=12)
        ano_table.add_column("Anomaly Issue", style="bold white", width=35)
        ano_table.add_column("Details & Forensic Explanation")

        for a in anomalies:
            ano_table.add_row(
                f"[{'red' if a['severity'] == 'HIGH' else 'yellow'}]{a['severity']}[/]",
                a['title'],
                f"{a['description']} ([cyan]{a.get('metric', '')}[/cyan])"
            )
        console.print(ano_table)
    else:
        console.print(Panel("[green][OK] No severe financial divergences (CFO/Net Income, Receivables, Inventory) detected.[/green]", border_style="green"))

    # 4. Regulatory Flags
    reg_flags = forensics.get("regulatory_flags", [])
    if reg_flags:
        reg_table = Table(title="[bold red]REGULATORY & AUDIT TEXT TRIGGERS (10-K / 10-Q)[/bold red]", box=box.ROUNDED, expand=True)
        reg_table.add_column("Severity", width=12)
        reg_table.add_column("Trigger", style="bold white", width=30)
        reg_table.add_column("Filing Excerpt", style="dim")

        for rf in reg_flags:
            reg_table.add_row(
                f"[bold red]{rf['severity']}[/bold red]",
                rf['title'],
                rf['excerpt']
            )
        console.print(reg_table)

    # 5. Tone & Sentiment
    sentiment = forensics.get("sentiment")
    if sentiment:
        tone_text = (
            f"Tone: [bold cyan]{sentiment.get('tone')}[/bold cyan] | "
            f"Uncertainty: [yellow]{sentiment.get('uncertainty_pct')}%[/yellow] | "
            f"Litigious: [red]{sentiment.get('litigious_pct')}%[/red] | "
            f"Negative: [red]{sentiment.get('negative_pct')}%[/red] | "
            f"Positive: [green]{sentiment.get('positive_pct')}%[/green] (Total words: {sentiment.get('total_words'):,})"
        )
        console.print(Panel(tone_text, title="Loughran-McDonald Financial Sentiment (Item 1A / MD&A)", border_style="blue"))

    # 6. Filing Delta
    diff = data.get("diff_analysis")
    if diff:
        diff_text = (
            f"Similarity to Prior 10-K: [bold cyan]{diff.get('similarity_pct')}%[/bold cyan] | "
            f"Substantive Additions: [green]+{diff.get('added_count')}[/green] sentences | "
            f"Deletions: [red]-{diff.get('removed_count')}[/red] sentences"
        )
        console.print(Panel(diff_text, title="YoY Filing Delta (Item 1A Risk Factors)", border_style="magenta"))

def main():
    parser = argparse.ArgumentParser(description="ARGUS Financial Forensics Terminal")
    parser.add_argument("ticker", nargs="?", default="NVDA", help="Stock ticker (e.g. NVDA, AAPL, TSLA)")
    args = parser.parse_args()

    console.print(f"[bold cyan]Querying SEC EDGAR & Market feeds for {args.ticker.upper()}...[/bold cyan]")
    engine = ArgusEngine()
    result = engine.analyze_ticker(args.ticker)

    if "error" in result and not result.get("forensics"):
        console.print(f"[bold red]Error: {result['error']}[/bold red]")
        sys.exit(1)

    print_cli_report(result)

if __name__ == "__main__":
    main()
