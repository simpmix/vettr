import argparse
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from vettr.engine import VettrEngine

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
    header_text.append(f"VETTR RESEARCH TERMINAL // {ticker} : {mkt.get('name', '')}\n", style="bold cyan")
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

    # 7. Reverse DCF Valuation & Executive Synthesis
    val = data.get("valuation_model", {})
    if val:
        val_text = (
            f"Implied 10-Yr FCF CAGR: [bold yellow]{val.get('implied_growth_10yr_pct')}%[/bold yellow] | "
            f"Est. FCF: [cyan]${val.get('fcf_estimate'):,.0f}[/cyan] | "
            f"FCF Yield: [white]{val.get('fcf_yield_pct')}%[/white] | "
            f"Valuation: [bold]{val.get('valuation_verdict')}[/bold]"
        )
        console.print(Panel(val_text, title="Reverse DCF Implied Expectations", border_style="cyan"))

    synthesis = data.get("executive_synthesis")
    if synthesis:
        console.print(Panel(f"[italic]{synthesis}[/italic]", title="[bold white]Executive Forensic Auditor Synthesis[/bold white]", border_style="white"))

def run_cli_compare(tickers_str: str):
    tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()][:5]
    console.print(f"[bold cyan]Interrogating SEC EDGAR filings for peer group: {', '.join(tickers)}...[/bold cyan]\n")

    engine = VettrEngine()
    comp_table = Table(title="[bold yellow]VETTR PEER FORENSIC COMPARISON[/bold yellow]", box=box.ROUNDED, expand=True)
    comp_table.add_column("Ticker", style="bold white", width=8)
    comp_table.add_column("Name", width=22)
    comp_table.add_column("Price", style="cyan", justify="right", width=10)
    comp_table.add_column("Risk Score", justify="center", width=12)
    comp_table.add_column("Beneish M", justify="center", width=12)
    comp_table.add_column("Altman Z", justify="center", width=10)
    comp_table.add_column("Piotroski", justify="center", width=10)
    comp_table.add_column("Implied Growth", justify="right", width=14)

    for t in tickers:
        try:
            res = engine.analyze_ticker(t)
            mkt = res.get("market_data", {})
            f = res.get("forensics", {})
            risk = res.get("risk_score", 0)
            b = f.get("beneish_m_score") or {}
            z = f.get("altman_z_score") or {}
            pi = f.get("piotroski_f_score") or {}
            val = res.get("valuation_model") or {}

            r_color = "green" if risk < 30 else ("yellow" if risk < 60 else "red")
            b_color = "red" if b.get("is_manipulator") else "green"

            comp_table.add_row(
                t,
                mkt.get("name", t)[:22],
                f"${mkt.get('current_price', 0):.2f}",
                f"[{r_color}]{risk} / 100[/{r_color}]",
                f"[{b_color}]{b.get('score', 'N/A')}[/{b_color}]",
                str(z.get("score", "N/A")),
                f"{pi.get('score', 'N/A')}/9" if pi.get('score') is not None else "N/A",
                f"{val.get('implied_growth_10yr_pct', 'N/A')}%"
            )
        except Exception as e:
            comp_table.add_row(t, f"Error: {e}", "-", "-", "-", "-", "-", "-")

    console.print(comp_table)

def main():
    parser = argparse.ArgumentParser(description="VETTR Financial Forensics Terminal")
    parser.add_argument("ticker", nargs="?", default="NVDA", help="Stock ticker (e.g. NVDA, AAPL, TSLA)")
    parser.add_argument("--compare", help="Compare multiple tickers (e.g. --compare NVDA,AMD,INTC)")
    parser.add_argument("--audit", action="store_true", help="Print deep accounting forensic metrics (Sloan, DSO, DIO)")
    args = parser.parse_args()

    if args.compare:
        run_cli_compare(args.compare)
        return

    console.print(f"[bold cyan]Querying SEC EDGAR & Market feeds for {args.ticker.upper()}...[/bold cyan]")
    engine = VettrEngine()
    result = engine.analyze_ticker(args.ticker)

    if "error" in result and not result.get("forensics"):
        console.print(f"[bold red]Error: {result['error']}[/bold red]")
        sys.exit(1)

    print_cli_report(result)

    if args.audit:
        gm = result.get("growth_metrics", {})
        acc_table = Table(title="[bold yellow]DEEP ACCOUNTING FORENSICS & WORKING CAPITAL[/bold yellow]", box=box.ROUNDED)
        acc_table.add_column("Metric", style="bold white", width=30)
        acc_table.add_column("Value", style="cyan", width=15)
        acc_table.add_column("Benchmark / Interpretation")

        sloan_pct = gm.get("sloan_accrual_pct")
        acc_table.add_row(
            "Sloan Accrual Ratio",
            f"{sloan_pct}%" if sloan_pct is not None else "N/A",
            gm.get("sloan_status", "Normal")
        )
        acc_table.add_row(
            "Days Sales Outstanding (DSO)",
            f"{gm.get('dso_days')} days" if gm.get('dso_days') is not None else "N/A",
            "Speed of receivables cash collection"
        )
        acc_table.add_row(
            "Days Inventory Outstanding (DIO)",
            f"{gm.get('dio_days')} days" if gm.get('dio_days') is not None else "N/A",
            "Inventory turnover & obsolescence risk"
        )
        acc_table.add_row(
            "Cash Conversion % (CFO / NI)",
            f"{gm.get('cash_conversion_pct')}%" if gm.get('cash_conversion_pct') is not None else "N/A",
            "Earnings backed by physical cash flow (>100% ideal)"
        )
        acc_table.add_row(
            "Return on Invested Capital (ROIC)",
            f"{gm.get('roic_pct')}%" if gm.get('roic_pct') is not None else "N/A",
            "True economic engine return after capital charge"
        )
        console.print(acc_table)

if __name__ == "__main__":
    main()
