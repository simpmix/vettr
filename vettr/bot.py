"""
VETTR Viral Distribution & Forensic Teardown Generator.
Generates publication-ready social threads (FinTwit/X, Reddit, Show HN)
and daily forensic due-diligence briefs to market VETTR organically.
"""

import argparse
import sys
from typing import Any, Dict
from vettr.engine import VettrEngine

# Ensure Windows PowerShell console can output UTF-8 without charmap errors
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def generate_twitter_thread(report: Dict[str, Any]) -> str:
    ticker = report.get("ticker", "UNKNOWN")
    mkt = report.get("market_data", {})
    forensics = report.get("forensics", {})
    risk = report.get("risk_score", 0)
    b = forensics.get("beneish_m_score") or {}
    z = forensics.get("altman_z_score") or {}
    pi = forensics.get("piotroski_f_score") or {}
    gm = report.get("growth_metrics", {})
    val = report.get("valuation_model", {})
    anomalies = forensics.get("anomalies", [])
    diff = report.get("diff_analysis") or {}

    thread = []

    # Tweet 1: Hook
    thread.append(
        f"🧵 1/7 Wall Street pays $24,000/year for Bloomberg terminals.\n\n"
        f"We just ran ${ticker} ({mkt.get('name', ticker)}) through VETTR—our 100% free open-source financial forensics terminal interrogating public SEC EDGAR data.\n\n"
        f"Here is what the audited 10-K filings reveal about their accounting quality 👇"
    )

    # Tweet 2: Forensic Scorecard
    b_flag = "⚠️ Manipulator Flag" if b.get("is_manipulator") else "✅ Normal Accounting"
    thread.append(
        f"2/7 Quantitative Forensic Scorecard for ${ticker}:\n\n"
        f"• Beneish M-Score: {b.get('score', 'N/A')} [{b_flag}]\n"
        f"• Altman Z-Score: {z.get('score', 'N/A')} [{z.get('zone', 'N/A')}]\n"
        f"• Piotroski F-Score: {pi.get('score', 'N/A')}/9 [{pi.get('rating', 'N/A')}]\n"
        f"• Composite Forensic Risk: {risk}/100"
    )

    # Tweet 3: Accruals & Sloan Anomaly
    sloan_pct = gm.get("sloan_accrual_pct", 0)
    dso = gm.get("dso_days", "N/A")
    cash_conv = gm.get("cash_conversion_pct", "N/A")
    thread.append(
        f"3/7 Earnings Quality & The Sloan Accrual Anomaly (Sloan 1996):\n\n"
        f"Are profits backed by actual cash flow, or paper journal entries?\n\n"
        f"• Sloan Accrual Ratio: {sloan_pct}%\n"
        f"• Cash Conversion (CFO/Net Income): {cash_conv}%\n"
        f"• Days Sales Outstanding (DSO): {dso} days\n"
        f"• Status: {gm.get('sloan_status', 'Normal')}"
    )

    # Tweet 4: Reverse DCF Expectations
    thread.append(
        f"4/7 Reverse DCF: What is the market currently pricing in?\n\n"
        f"Instead of guessing the future, Reverse DCF calculates the exact growth rate required to justify today's ${mkt.get('current_price', 0):.2f} price:\n\n"
        f"• Implied 10-Yr FCF CAGR: {val.get('implied_growth_10yr_pct')}%/year\n"
        f"• Est. FCF (TTM): ${val.get('fcf_estimate', 0):,.0f}\n"
        f"• Valuation Verdict: {val.get('valuation_verdict')}"
    )

    # Tweet 5: 10-K Diff & Hidden Changes
    diff_text = f"Substantive additions: +{diff.get('added_count', 0)} sentences, struck: -{diff.get('removed_count', 0)} sentences." if diff else "No prior diff available."
    thread.append(
        f"5/7 Year-over-Year 10-K Risk Factor Disclosures:\n\n"
        f"When companies get subpoenaed or lose major clients, they quietly slip disclaimers into Item 1A.\n\n"
        f"• Textual Similarity: {diff.get('similarity_pct', 'N/A')}%\n"
        f"• {diff_text}"
    )

    # Tweet 6: Anomalies & Verdict
    ano_text = f"Surfaced {len(anomalies)} balance sheet anomaly." if anomalies else "Zero severe balance sheet decouplings detected."
    thread.append(
        f"6/7 Executive Forensic Verdict for ${ticker}:\n\n"
        f"{report.get('executive_synthesis', 'No severe red flags surfaced.')}\n\n"
        f"Accrual Decoupling Check: {ano_text}"
    )

    # Tweet 7: CTA & GitHub Link
    thread.append(
        f"7/7 VETTR is 100% free, open-source, and runs locally with zero cloud bills.\n\n"
        f"Every line of SEC XBRL data is public. Stop paying thousands for closed platforms.\n\n"
        f"⭐ Star the project on GitHub:\n"
        f"https://github.com/simpmix/vettr\n\n"
        f"#FinTwit #Stocks #Investing #OpenSource #Python #AlgorithmicTrading ${ticker}"
    )

    return "\n\n" + ("=" * 60) + "\n\n".join(thread)

def generate_reddit_post(report: Dict[str, Any]) -> str:
    ticker = report.get("ticker", "UNKNOWN")
    mkt = report.get("market_data", {})
    forensics = report.get("forensics", {})
    risk = report.get("risk_score", 0)
    b = forensics.get("beneish_m_score") or {}
    z = forensics.get("altman_z_score") or {}
    pi = forensics.get("piotroski_f_score") or {}
    gm = report.get("growth_metrics", {})
    val = report.get("valuation_model", {})

    post = f"""
# Title: I built an open-source terminal to audit SEC filings for ${ticker} (Beneish M-Score, Altman Z, Sloan Accruals, Reverse DCF)

Hey everyone,

Institutional terminals like Bloomberg cost $24,000/year, but virtually all core financial data—10-Ks, 10-Qs, 8-Ks, XBRL financial facts, and Form 4 insider transactions—is legally mandated to be 100% free and open via U.S. SEC EDGAR.

I built **VETTR**, a local open-source financial forensics workstation that interrogates SEC filings using quantitative peer-reviewed accounting models.

Here is the deep forensic teardown for **${ticker} ({mkt.get('name', ticker)})**:

---

### 1. Quantitative Forensic Benchmark Scorecard
* **Beneish M-Score (Earnings Manipulation):** `{b.get('score', 'N/A')}` (Benchmark threshold: < -1.78. Assessment: **{b.get('status', 'N/A')}**)
* **Altman Z-Score (Bankruptcy / Distress):** `{z.get('score', 'N/A')}` (Assessment: **{z.get('zone', 'N/A')}**)
* **Piotroski F-Score (9-Factor Fundamental Strength):** `{pi.get('score', 'N/A')}/9` (Rating: **{pi.get('rating', 'N/A')}**)
* **Composite Forensic Risk Rating:** `{risk} / 100`

---

### 2. Sloan Accrual Anomaly & Working Capital Telemetry
In 1996, Richard Sloan published landmark empirical research in *The Accounting Review* showing companies with high non-cash earnings accruals (> 10% of assets) suffer massive subsequent stock underperformance when earnings mean-revert.
* **Sloan Accrual Ratio:** `{gm.get('sloan_accrual_pct', 'N/A')}%`
* **Cash Conversion (CFO / Net Income):** `{gm.get('cash_conversion_pct', 'N/A')}%`
* **Days Sales Outstanding (DSO):** `{gm.get('dso_days', 'N/A')} days`
* **Return on Invested Capital (ROIC):** `{gm.get('roic_pct', 'N/A')}%`

---

### 3. Reverse DCF: What Expectations Are Priced In?
Instead of forecasting the future with arbitrary inputs, Reverse DCF answers: *What annual Free Cash Flow growth rate does today's stock price (${mkt.get('current_price', 0):.2f}) require over the next decade?*
* **Implied 10-Year Annual FCF CAGR:** `{val.get('implied_growth_10yr_pct')}%`
* **Estimated Free Cash Flow (TTM):** `${val.get('fcf_estimate', 0):,.0f}`
* **Free Cash Flow Yield:** `{val.get('fcf_yield_pct')}%`
* **Market Expectation Verdict:** **{val.get('valuation_verdict')}**

---

### 4. Executive Forensic Synthesis
> *"{report.get('executive_synthesis', 'Accounting telemetry verified against SEC EDGAR records.')}"*

---

Everything runs 100% locally with Python, FastAPI, and SEC EDGAR with $0 cloud fees. The code is completely open-source:

GitHub Repository: https://github.com/simpmix/vettr

Would love your feedback on additional forensic accounting ratios or anomaly detectors you'd like to see added!
"""
    return post.strip()

def generate_hacker_news_post() -> str:
    return """
Title: Show HN: VETTR – Open-source local financial forensics terminal for SEC EDGAR

URL / Link: https://github.com/simpmix/vettr

Text:
Hi HN!

Bloomberg and FactSet charge upwards of $24,000/seat/year. Yet all core US corporate disclosure data—audited 10-K annual reports, 8-K material events, Form 4 insider transactions, and multi-year XBRL financial facts—is legally mandated to be 100% free and publicly accessible from the U.S. SEC EDGAR archive.

I built VETTR, an autonomous, local-first financial forensics terminal in Python & FastAPI that interrogates the SEC EDGAR API directly to detect accounting manipulation, distress risks, and disclosure alterations.

Key Features:
1. Beneish M-Score (1999) – 8-variable probabilistic accounting regression to detect aggressive revenue recognition and earnings manipulation.
2. Altman Z-Score (1968) – Solvency discriminant analysis predicting 24-month bankruptcy probability.
3. Piotroski F-Score (2000) – 9-signal discrete binary metric of financial discipline.
4. Sloan Accrual Anomaly (1996) – Measuring non-cash accruals vs operating cash flow.
5. Reverse DCF Model & Sensitivity Matrix – Inverting discounted cash flows to calculate the exact 10-year FCF expansion the market is pricing in.
6. 10-K Text Delta Differ – Sentence-level semantic diffing of Item 1A Risk Factors between consecutive fiscal years to catch silently inserted subpoenas or client losses.
7. Continuous Stock Exchange Ticker Tape – Streaming quotes for S&P 500, Nasdaq 100, Dow 30, and volume leaders with 15-second caching.
8. Universal Index of all 10,443 U.S. public companies in SEC EDGAR.

It runs locally with zero external API keys and $0 cloud infrastructure costs. The UI is designed with an institutional dark palette and strict tabular Calibri figures.

Repo: https://github.com/simpmix/vettr

I'd love feedback on the models, XBRL parsing, and features.
"""

def main():
    parser = argparse.ArgumentParser(description="VETTR Viral Distribution & Content Engine")
    parser.add_argument("--ticker", default="NVDA", help="Ticker to generate teardown for (e.g. NVDA, SMCI, TSLA)")
    parser.add_argument("--platform", choices=["twitter", "reddit", "hn"], default="twitter", help="Distribution target platform")
    parser.add_argument("--launch-hn", action="store_true", help="Print Show HN launch post")
    args = parser.parse_args()

    if args.launch_hn or args.platform == "hn":
        print(generate_hacker_news_post())
        return

    engine = VettrEngine()
    print(f"Generating forensic breakdown for {args.ticker.upper()}...", file=sys.stderr)
    report = engine.analyze_ticker(args.ticker)

    if args.platform == "twitter":
        print(generate_twitter_thread(report))
    elif args.platform == "reddit":
        print(generate_reddit_post(report))

if __name__ == "__main__":
    main()
