# ⬡ ARGUS TERMINAL
### Autonomous Regulatory & Financial Intelligence Engine
> **The Open-Source Bloomberg Alternative for Forensic Accounting, SEC EDGAR Disclosures & Anomaly Detection.**

[![Status](https://img.shields.io/badge/Status-Live%20Engine-00F090?style=for-the-badge)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.13+-00D4FF?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SEC EDGAR](https://img.shields.io/badge/Data-US%20SEC%20EDGAR%20XBRL-FFB020?style=for-the-badge)](https://sec.gov/edgar)
[![License](https://img.shields.io/badge/License-Apache%202.0-blueviolet?style=for-the-badge)](#)

---

## 🏛️ Executive Summary

Institutional financial terminals like **Bloomberg**, **FactSet**, and **AlphaSense** charge upwards of **$24,000 per user per year**. Yet, the foundation of all US financial intelligence—audited 10-K filings, 10-Q quarterly reports, 8-K material event disclosures, and XBRL company facts—is **100% free and publicly mandated by the US Securities and Exchange Commission (SEC)**.

**ARGUS** bridges this gap. It is an autonomous, local-first financial forensics and regulatory intelligence workstation that interrogates the SEC EDGAR archive to surface:
1. **Earnings Manipulation Risk** (via the 8-variable Beneish M-Score).
2. **Insolvency & Default Hazards** (via the Altman Z-Score).
3. **Fundamental Financial Health** (via the 9-point Piotroski F-Score).
4. **Accounting & Accrual Anomalies** (Operating cash flow decoupling, DSO channel stuffing, inventory bloat).
5. **Regulatory Red Flag Triggers** (Automated scanning for subpoenas, restatements, internal control weaknesses).
6. **Loughran-McDonald Financial Sentiment** (Quantifying hedging language, litigious density, and management uncertainty).
7. **YoY 10-K Section Delta / Semantic Diff** (Pinpointing newly inserted or silently removed risk factors).

---

## ⚡ Architecture & Tech Stack

ARGUS requires **$0 in cloud hosting bills** to operate, utilizing official public SEC REST APIs, local headless extraction, and a high-performance terminal architecture:

```
┌────────────────────────────────────────────────────────┐
│                   ARGUS WEB TERMINAL                   │
│         (High-Density Dark HUD + Keyboard Shortcuts)    │
└───────────────────────────▲────────────────────────────┘
                            │ REST / JSON
┌───────────────────────────┴────────────────────────────┐
│                    FastAPI Web Core                    │
├────────────────────────────────────────────────────────┤
│                     ARGUS ENGINE                       │
│  ┌───────────────────────┬───────────────────────────┐ │
│  │   SEC EDGAR CLIENT    │   FORENSIC SUITE          │ │
│  │   • CIK Resolver      │   • Beneish M-Score       │ │
│  │   • XBRL CompanyFacts │   • Altman Z-Score        │ │
│  │   • Submissions / 8-K │   • Piotroski F-Score     │ │
│  ├───────────────────────┼───────────────────────────┤ │
│  │   DISCLOSURE PARSER   │   ANOMALY DETECTOR        │ │
│  │   • Item 1A Risk Diff │   • CFO / Net Income Gap  │ │
│  │   • Item 7 MD&A       │   • Receivables Surge     │ │
│  │   • LM Tone Sentiment │   • Regulatory Triggers   │ │
│  └───────────────────────┴───────────────────────────┘ │
└───────────────────────────▲────────────────────────────┘
                            │ Free Public Feeds
        ┌───────────────────┴───────────────────┐
        │  • SEC EDGAR (data.sec.gov)           │
        │  • Yahoo Finance (Real-time Market)   │
        └───────────────────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Launch the Live Web Terminal (Recommended)
Double-click `run.py` or execute:
```bash
python run.py
```
This automatically boots the server and opens your browser at:
👉 **`http://localhost:8000`**

### 2. Run Instant CLI Forensic Scans
For terminal power users and quants:
```bash
# Scan NVIDIA
python -m argus.cli NVDA

# Scan Apple
python -m argus.cli AAPL

# Scan Tesla
python -m argus.cli TSLA
```

---

## 🔬 Forensic Models Built into ARGUS

### 1. Beneish M-Score (Earnings Manipulation)
Developed by Prof. Messod Beneish, this probabilistic model evaluates 8 distinct balance sheet and income statement ratios:
* **DSRI** (Days Sales in Receivables Index)
* **GMI** (Gross Margin Index)
* **AQI** (Asset Quality Index)
* **SGI** (Sales Growth Index)
* **DEPI** (Depreciation Rate Index)
* **SGAI** (SG&A Expense Index)
* **LVGI** (Leverage Ratio Index)
* **TATA** (Total Accruals to Total Assets)

$$\text{M-Score} = -4.84 + 0.920 \cdot \text{DSRI} + 0.528 \cdot \text{GMI} + 0.404 \cdot \text{AQI} + 0.892 \cdot \text{SGI} + 0.115 \cdot \text{DEPI} - 0.172 \cdot \text{SGAI} + 4.037 \cdot \text{TATA} + 0.0327 \cdot \text{LVGI}$$

> **Interpretation:** Scores **greater than -1.78** indicate an elevated statistical probability of earnings manipulation.

### 2. Altman Z-Score (Credit & Insolvency Distress)
Evaluates working capital, retained earnings, EBIT, equity capitalization, and asset turnover to predict bankruptcy within 24 months:
* **Safe Zone:** $Z > 2.99$ (Low distress probability)
* **Grey Zone:** $1.81 \le Z \le 2.99$ (Moderate risk)
* **Distress Zone:** $Z < 1.81$ (High insolvency hazard)

### 3. Loughran-McDonald Financial Lexicon Tone
Standard English NLP sentiment classifiers miscategorize financial vocabulary (e.g. "liability", "tax", "cost"). ARGUS utilizes the **Loughran-McDonald Financial Dictionary** to track:
* **Uncertainty & Hedging Density**
* **Litigious Vocabulary Rate**
* **Constraining Covenants**
* **Net Sentiment Polarity**

---

## 💰 How to Turn This Into a Lucrative Business ($0 Upfront)

1. **Commercial Open Source Software (COSS):**
   * Host the open-source repo on GitHub.
   * Monetize with an **Enterprise Cloud Hosted Version** ($49/month or $499/year for equity analysts, retail quants, and short-sellers).
2. **Paid Substack / Subscriptions for "Forensic Short Alerts":**
   * Run ARGUS across the S&P 500 or Russell 2000 weekly to detect stocks exhibiting M-Score anomalies or sudden Risk Factor insertions.
   * Publish a weekly newsletter: *"The Forensic Insider"* charging $50–$100/mo.
3. **Automated API Access:**
   * Charge algorithmic funds and fintech startups for REST API access to parsed SEC risk diffs and Beneish ratings via RapidAPI or Stripe.
