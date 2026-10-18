# VETTR
### Autonomous Financial Forensics & Regulatory Intelligence Workstation
> **The open-source Bloomberg alternative for SEC EDGAR accounting forensics, Beneish earnings manipulation models, and filing diffs.**

[![Status](https://img.shields.io/badge/Status-Active%20Engine-10B981?style=flat-square)](https://github.com/simpmix/vettr)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-FAFAFA?style=flat-square&logo=python&logoColor=black)](https://python.org)
[![SEC EDGAR](https://img.shields.io/badge/Data-US%20SEC%20EDGAR%20XBRL-06B6D4?style=flat-square)](https://sec.gov/edgar)
[![License](https://img.shields.io/badge/License-Apache%202.0-FAFAFA?style=flat-square)](#)

---

## Executive Overview

Institutional financial platforms like Bloomberg, FactSet, and AlphaSense charge upwards of **$24,000/seat/year**. Yet the foundation of all US financial intelligence—audited 10-K annual reports, 10-Q quarterly reports, 8-K material event filings, and XBRL company facts—is **100% free and publicly mandated by the US Securities and Exchange Commission (SEC)**.

**VETTR** is a local-first, zero-cloud-cost financial forensics terminal that interrogates the SEC EDGAR archive to surface accounting anomalies, corporate governance risks, and hidden disclosure modifications before the market catches on.

---

## Core Capabilities

1. **Beneish M-Score (Messod Beneish, 1999)**
   * Complete 8-factor probabilistic earnings manipulation detection model:
     - Days Sales in Receivables Index (DSRI)
     - Gross Margin Index (GMI)
     - Asset Quality Index (AQI)
     - Sales Growth Index (SGI)
     - Depreciation Index (DEPI)
     - SG&A Expense Index (SGAI)
     - Leverage Index (LVGI)
     - Total Accruals to Total Assets (TATA)
   * Statistically flags companies with M-Score > -1.78.

2. **Altman Z-Score (Edward Altman, 1968)**
   * Empirical discriminant analysis predicting default and insolvency distress for public manufacturing and service corporations within 24 months.

3. **Piotroski F-Score (Joseph Piotroski, 2000)**
   * 9-signal discrete fundamental health scorecard measuring profitability momentum, liquidity, and operational leverage.

4. **DuPont 3-Way & 5-Way Return on Equity Engine**
   * Deconstructs ROE across Net Profit Margin, Asset Turnover, and Financial Leverage across all historical fiscal years.

5. **Item 1A Risk Factors Semantic Diff**
   * Sentence-by-sentence comparison of consecutive 10-K filings to expose silently inserted regulatory inquiries, customer losses, or struck disclaimers.

6. **Loughran-McDonald Financial NLP Lexicon**
   * Domain-specific sentiment analysis tracking litigious word density, hedging, uncertainty, and constraining covenants.

7. **SEC Form 4 Insider Radar**
   * Real-time monitoring of C-suite (CEO, CFO, Director) open-market transactions and cluster sales.

8. **Sloan Accrual Anomaly & Working Capital Forensics (Richard Sloan, 1996)**
   * Detects aggressive non-cash earnings decoupling:
     - Sloan Accrual Ratio = (Net Income - Operating Cash Flow) / Total Assets
     - Days Sales Outstanding (DSO) & YoY expansion (channel-stuffing flag)
     - Days Inventory Outstanding (DIO) (inventory bloat & obsolescence alert)
     - Cash Conversion Ratio (Operating Cash Flow / Net Income)

9. **Form 8-K Real-Time Material Event Registry**
   * Item code extraction for urgent disclosures:
     - Item 5.02: Departure of Principal Officers / Directors
     - Item 4.02: Non-Reliance on Previously Issued Financial Statements (Restatements)
     - Item 4.01: Changes in Certifying Accountants
     - Item 2.02: Results of Operations / Unscheduled Earnings

10. **Interactive Reverse DCF & Sensitivity Matrix**
    * Inverts standard DCF to determine what annual Free Cash Flow expansion the stock's current price requires.
    * Interactive 3x3 Sensitivity Matrix across variable WACC Discount Rates (8%, 10%, 12%) and Terminal Growth (2%, 3%, 4%).

11. **Head-to-Head Peer Comparison & Screener**
    * Side-by-side benchmarking of multiple equities with ranked risk scoring across 9 sector presets.

12. **Institutional Dual Export & Print Memorandums**
    * 1-Click generation of publication-ready Due Diligence Memorandums in Markdown, structured GAAP financial data in CSV/JSON, and clean PDF report formatting.

13. **Continuous Stock Exchange Pulse & Live Ticker Tape**
    * 15-second background polling of market indices (`SPY`, `QQQ`, `DIA`, `IWM`, `^VIX`) and active volume leaders with real-time delta badges and ticker-click switching.

14. **Interactive High-DPI Vector OHLCV Trajectory & Volume Chart**
    * Lightweight, zero-dependency SVG financial chart with customizable horizons (1M, 3M, 6M, 1Y, 5Y), volume accumulation histogram, and interactive hover crosshair inspection.

15. **In-Terminal SEC EDGAR Document Reader Modal**
    * Stream, view, and live-filter Form 10-K, Form 8-K, and Form 4 documents right inside the terminal without losing your workstation context or wrestling with slow government archives.

16. **Pro Financial Hotkeys & Universal Company Index**
    * Complete index of all 10,443 U.S. public equities with instant fuzzy autocomplete, alongside institutional hotkeys (`/` search, `1-9` tabs, `C` copy brief, `P` print PDF, `M` toggle chart, `Esc` close modal).

---

## Quickstart

### Launch the Workstation (Recommended)
```bash
python run.py
```
Opens the live institutional workstation at:
👉 **`http://localhost:8000`**

### Command-Line Interface (Quants & Terminal Users)
```bash
# Standard forensic scan
python -m vettr.cli NVDA

# Deep accounting forensics & working capital audit (Sloan, DSO, DIO, Reverse DCF)
python -m vettr.cli NVDA --audit

# Side-by-side peer comparison
python -m vettr.cli --compare NVDA,AMD,INTC,TSM

# Run batch screener across watchlists
python -m vettr.screener --list mega_tech
python -m vettr.screener --list semis
```

### Run Automated Test Suite
```bash
python -m unittest discover tests/
```

---

## Architecture

VETTR runs 100% locally with **$0 in cloud bills**:

```
┌────────────────────────────────────────────────────────┐
│                   VETTR WORKSTATION                    │
│   (Swiss-Brutalist HUD • Autocomplete • Calibri Tnum)  │
└───────────────────────────▲────────────────────────────┘
                            │ REST / JSON
┌───────────────────────────┴────────────────────────────┐
│                    FastAPI Web Core                    │
├────────────────────────────────────────────────────────┤
│                      VETTR ENGINE                      │
│  ┌───────────────────────┬───────────────────────────┐ │
│  │   SEC EDGAR CLIENT    │   FORENSIC SUITE          │ │
│  │   • CIK Resolver      │   • Beneish M-Score       │ │
│  │   • XBRL CompanyFacts │   • Altman Z-Score        │ │
│  │   • Form 4 Insiders   │   • Piotroski F-Score     │ │
│  │   • 10-K Submissions  │   • DuPont 5-Way Engine   │ │
│  ├───────────────────────┼───────────────────────────┤ │
│  │   DISCLOSURE PARSER   │   VALUATION & SCREENER    │ │
│  │   • Item 1A Risk Diff │   • Reverse DCF Model     │ │
│  │   • LM Tone Analysis  │   • Peer Group Comparison │ │
│  │   • Accrual Anomalies │   • Batch Anomaly Radar   │ │
│  └───────────────────────┴───────────────────────────┘ │
└───────────────────────────▲────────────────────────────┘
                            │ Free Public Feeds
        ┌───────────────────┴───────────────────┐
        │  • U.S. SEC EDGAR (data.sec.gov)      │
        │  • Real-Time Market Data Provider     │
        └───────────────────────────────────────┘
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for architecture guidelines, pull request protocols, and development setup.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
