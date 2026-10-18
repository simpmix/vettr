# VETTR // Viral Go-To-Market & Distribution Master Playbook
### Zero-Cost Growth Strategy to 10,000+ GitHub Stars & Institutional Community

> **Core Value Proposition:** Why pay Bloomberg or FactSet $24,000/seat/year when all U.S. financial intelligence (audited 10-Ks, 10-Qs, 8-Ks, Form 4 insider trades, and multi-year XBRL financials) is 100% free and publicly mandated by the U.S. SEC?

---

## 1. Executive Channel Matrix & Priority

| Priority | Channel | Target Audience | Expected Reach | Conversion Goal |
| :--- | :--- | :--- | :--- | :--- |
| **P0** | **Hacker News (Show HN)** | Developers, Quants, Tech Founders | 50k - 150k impressions | 1,000 - 3,000 Stars (Front page) |
| **P0** | **FinTwit / X (Twitter)** | Value Investors, Short Sellers, Quants | 10k - 100k views/thread | Viral retweets & hedge fund users |
| **P1** | **Reddit (5 Subreddits)** | r/algotrading, r/Python, r/stocks, r/wsb | 100k+ total views | 500 - 1,500 Stars |
| **P1** | **Product Hunt** | Indie Hackers, Finance Tech enthusiasts | Top 5 Product of the Day | 300 - 800 Stars + Newsletter features |
| **P2** | **Awesome-Lists PRs** | Open-source Python & Quant ecosystem | Passive continuous discovery | 50 - 100 Stars/month ongoing |

---

## 2. Channel 1: The Hacker News "Show HN" Playbook

### Timing:
* **Best Day:** Tuesday or Wednesday
* **Best Time:** 8:00 AM – 9:00 AM US Eastern Time (1:00 PM – 2:00 PM UTC)

### Title:
```
Show HN: VETTR – Open-source local financial forensics terminal for SEC EDGAR
```

### Exact Submission Copy:
```markdown
Hi HN!

Institutional terminals like Bloomberg and FactSet charge upwards of $24,000 per seat per year. Yet the foundation of all US financial intelligence—audited 10-K annual reports, 8-K material events, Form 4 insider transactions, and multi-year XBRL financial facts—is legally mandated by the U.S. SEC to be 100% free and open via data.sec.gov.

I built VETTR (https://github.com/simpmix/vettr), an autonomous local-first financial forensics terminal in Python and FastAPI that interrogates the SEC EDGAR archive to detect accounting anomalies, earnings manipulation, and hidden disclosure modifications.

Key Features:
1. Beneish M-Score (1999) – 8-variable probabilistic accounting regression to detect aggressive revenue recognition and earnings manipulation.
2. Altman Z-Score (1968) – Solvency discriminant analysis predicting 24-month bankruptcy probability.
3. Piotroski F-Score (2000) – 9-signal discrete binary metric of financial discipline.
4. Sloan Accrual Anomaly (1996) – Measuring non-cash accounting accruals vs cash from operations to catch earnings decoupling.
5. Reverse DCF Model & Sensitivity Matrix – Inverting discounted cash flows to calculate the exact 10-year FCF expansion the market is pricing in.
6. 10-K Text Delta Differ – Sentence-level semantic diffing of Item 1A Risk Factors between consecutive fiscal years to catch silently inserted subpoenas or client losses.
7. Continuous Stock Exchange Ticker Tape – Streaming quotes for S&P 500, Nasdaq 100, Dow 30, and volume leaders with 15-second caching.
8. Universal Index of all 10,443 U.S. public companies in SEC EDGAR.

Architecture:
- Backend: FastAPI, Python 3.11+, lxml, BeautifulSoup4, yfinance.
- Frontend: Zero-framework vanilla JS & CSS, institutional dark slate/obsidian palette, strict Calibri tabular numerics.
- 100% local, runs with `python run.py`, zero external API keys, $0 in cloud bills.

Repo: https://github.com/simpmix/vettr

I'd love feedback on the models, XBRL parsing, and features!
```

### Hacker News Execution Rules:
1. **Never ask friends to upvote from the same IP or network** (HN's spam filter will instantly shadowban).
2. Share the raw link to trusted friends via private message: *"I just launched VETTR on HN, search for it or check newest if you're interested!"*
3. **Reply to every single technical comment within 10 minutes** with thoughtful, technical depth (mentioning specific SEC XBRL tags, math behind Beneish, etc.). High comment activity keeps the post on the front page.

---

## 3. Channel 2: Reddit Multi-Subreddit Distribution

Execute these 4 posts over 48 hours:

### Post 1: r/algotrading & r/quant (1.8M members)
* **Title:** `I built an open-source SEC EDGAR quantitative forensics terminal in Python (Beneish M-Score, Altman Z, Sloan Accruals, Reverse DCF)`
* **Angle:** Focus on quantitative accounting literature, Sloan 1996 accrual anomaly, and algorithmic SEC XBRL parsing.
* **Content:** Use the automated output of `python -m vettr.bot --ticker NVDA --platform reddit`.

### Post 2: r/Python (1.3M members)
* **Title:** `Showcase: VETTR – An institutional-grade financial forensics workstation built with FastAPI & SEC EDGAR (10,443 companies indexed, $0 cloud costs)`
* **Angle:** Focus on clean Python architecture, sub-millisecond in-memory caching, web-scraping SEC archives without API keys, and dark-mode terminal aesthetics.

### Post 3: r/stocks & r/investing (7M+ members)
* **Title:** `How to audit a company's 10-K for earnings manipulation and hidden risks using free open-source forensic models (Beneish M-Score, Reverse DCF guide)`
* **Angle:** Educational due diligence guide for retail investors to avoid getting caught holding bags on aggressive accounting (like Enron, Super Micro, or Wirecard).

### Post 4: r/wallstreetbets (16M members)
* **Title:** `Built a free Bloomberg terminal alternative so we can check C-Suite insider dumping and fake accounting before buying 0DTE calls`
* **Angle:** Humorous, high-energy tone, highlighting Form 4 insider dumping and the Reverse DCF showing absurd growth expectations priced into meme stocks.

---

## 4. Channel 3: The FinTwit (X) Viral Content Engine

Use VETTR's automated bot (`python -m vettr.bot --ticker TICKER --platform twitter`) to publish 2-3 forensic teardowns per week.

### High-Impact Tickers to Teardown:
1. **$SMCI (Super Micro Computer)**: Focus on why Beneish M-Score and 10-K diffs caught accounting red flags before Ernst & Young resigned.
2. **$NVDA (Nvidia)**: Focus on the Reverse DCF implied growth (what annual FCF growth the market requires to justify a $5T market cap).
3. **$TSLA (Tesla)**: Focus on operating cash flow vs net income and Form 4 insider activity.
4. **$PLTR (Palantir)**: Focus on Sloan Accrual anomaly and sales growth index.

### FinTwit Best Practices:
* Attach 2 high-res screenshots of the VETTR workstation (the HUD + the Reverse DCF Sensitivity Matrix).
* Tag financial accounts: `@unusual_whales`, `@zerohedge`, `@bespokeinvest`, `@KoyfinCharts`, `#FinTwit`.
* Always include the GitHub repository link in the last tweet.

---

## 5. Channel 4: Product Hunt Launch Campaign

* **Product Name:** VETTR
* **Tagline:** The Open-Source Bloomberg Alternative for SEC Accounting Forensics
* **Categories:** Developer Tools, Open Source, Investing, Finance
* **Thumbnail / Logo:** Use the bespoke faceted geometric V monogram.
* **First Comment Checklist:**
  1. Story of why you built it: Frustration with $24k/year paywalls for public government data.
  2. The 100% local, zero-cloud-cost guarantee.
  3. Interactive demo link / GitHub URL.

---

## 6. Channel 5: Awesome-Lists Submissions

Submit PRs to these curated GitHub repositories to gain steady organic stars:
1. `vinta/awesome-python` -> Section: *Finance & Quant*
2. `wilsonfreitas/awesome-quant` -> Section: *Data Sources / Fundamentals*
3. `igorbarinov/awesome-fintech` -> Section: *Open Source Financial Terminals*
4. `awesome-selfhosted/awesome-selfhosted` -> Section: *Personal Finance & Investments*

PR Title format: `Add VETTR: Open-source SEC EDGAR financial forensics terminal`

---

## 7. Automated Content Generation CLI

Run these built-in commands at any time to generate instant viral marketing copy:

```bash
# Generate a complete 7-tweet viral FinTwit thread for any stock
python -m vettr.bot --ticker NVDA --platform twitter
python -m vettr.bot --ticker SMCI --platform twitter
python -m vettr.bot --ticker TSLA --platform twitter

# Generate an in-depth Reddit DD breakdown
python -m vettr.bot --ticker AAPL --platform reddit

# Output the Hacker News Show HN launch post
python -m vettr.bot --launch-hn
```
