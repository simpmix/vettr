import csv
import io
import logging
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from vettr.engine import VettrEngine
from vettr.forensics.metrics import ForensicMetrics
from vettr.market.provider import MarketDataProvider
from vettr.market.exchange_feed import ExchangePulseTracker
from vettr.screener import VettrScreener, PRESET_WATCHLISTS
from vettr.data.tickers import search_securities
from vettr.config import SERVER_HOST, SERVER_PORT

logger = logging.getLogger(__name__)

app = FastAPI(
    title="VETTR Financial Forensics Terminal",
    description="Autonomous SEC EDGAR Accounting Forensics & Intelligence Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = VettrEngine()
screener = VettrScreener()
STATIC_DIR = Path(__file__).resolve().parent / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "VETTR Terminal API online. Static frontend not found."}

@app.get("/api/market/pulse")
def get_market_pulse():
    """Live exchange telemetry: major indices and high-volume leaders."""
    return ExchangePulseTracker.get_exchange_pulse()

@app.get("/api/search")
def search_tickers(q: str = ""):
    """Instant search across pre-indexed securities database."""
    return search_securities(q)

@app.get("/api/analyze/{ticker}")
def analyze_ticker(ticker: str):
    """Run full quantitative forensic evaluation and SEC filing analysis."""
    try:
        report = engine.analyze_ticker(ticker)
        return report
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chart/{ticker}")
def get_chart_data(ticker: str, period: str = "6mo", interval: str = "1d"):
    """Fetches historical price candles and volume for interactive charting."""
    try:
        clean_ticker = ticker.strip().upper()
        candles = MarketDataProvider.get_historical_candles(clean_ticker, period=period, interval=interval)
        return {"ticker": clean_ticker, "period": period, "candles": candles}
    except Exception as e:
        logger.error(f"Error fetching chart for {ticker}: {e}")
        return {"ticker": ticker.upper(), "period": period, "candles": []}

@app.get("/api/sec-doc")
def get_sec_document(url: str):
    """Safely proxies and caches SEC filing document text/HTML for in-terminal reading."""
    try:
        if not url or not url.startswith("https://www.sec.gov/"):
            raise HTTPException(status_code=400, detail="Invalid SEC archive URL")
        
        content = engine.edgar.fetch_filing_content(url)
        # Cap at 600KB for responsive in-browser rendering
        is_truncated = False
        if len(content) > 600_000:
            content = content[:600_000]
            is_truncated = True

        return {
            "url": url,
            "truncated": is_truncated,
            "length": len(content),
            "content": content
        }
    except Exception as e:
        logger.error(f"Error fetching SEC doc {url}: {e}")
        return {"url": url, "error": str(e), "content": f"Unable to fetch SEC document: {e}"}

@app.get("/api/methodology/{metric_id}")
def get_methodology(metric_id: str):
    """Returns academic methodology, mathematical formula, and fraud case studies for a metric."""
    return ForensicMetrics.get_methodology_detail(metric_id.lower().strip())

@app.get("/api/commands")
def get_command_palette_actions():
    """Returns available omnibar quick actions for the Command Palette."""
    return {
        "tabs": [
            {"id": "tab-models", "title": "Forensic Models (Beneish, Altman, Piotroski, Montier)", "category": "Navigation"},
            {"id": "tab-solvency", "title": "Solvency, Liquidity & Capital Health Matrix", "category": "Navigation"},
            {"id": "tab-anomalies", "title": "Quantitative Accrual Divergences", "category": "Navigation"},
            {"id": "tab-valuation", "title": "Reverse DCF & Growth Implied Model", "category": "Navigation"},
            {"id": "tab-diff", "title": "Item 1A Risk Factors Disclosure Delta", "category": "Navigation"},
            {"id": "tab-dupont", "title": "DuPont 5-Way Return on Equity Engine", "category": "Navigation"},
            {"id": "tab-insiders", "title": "Form 4 Real-Time Insider Trading Radar", "category": "Navigation"},
            {"id": "tab-events-8k", "title": "Form 8-K Material Event Disclosures", "category": "Navigation"},
            {"id": "tab-compare", "title": "Head-to-Head Multi-Ticker Peer Benchmarking", "category": "Navigation"},
            {"id": "tab-screener", "title": "Institutional Multi-Sector Screener", "category": "Navigation"},
            {"id": "tab-financials", "title": "Audited Multi-Year GAAP Financial Series", "category": "Navigation"},
            {"id": "tab-archive", "title": "Chronological SEC EDGAR Filing Archive", "category": "Navigation"}
        ],
        "actions": [
            {"id": "copy_brief", "title": "Copy Executive Forensic Brief to Clipboard", "shortcut": "C", "category": "Action"},
            {"id": "print_pdf", "title": "Print / Export Due Diligence PDF", "shortcut": "P", "category": "Action"},
            {"id": "export_dossier", "title": "Export Markdown Due Diligence Dossier (.md)", "shortcut": "D", "category": "Action"},
            {"id": "export_csv", "title": "Export Audited Financial Statements to CSV", "shortcut": "S", "category": "Action"},
            {"id": "export_json", "title": "Download Full Raw Machine-Readable JSON", "shortcut": "J", "category": "Action"},
            {"id": "toggle_chart", "title": "Toggle Candlestick vs Area Price Chart", "shortcut": "M", "category": "Action"}
        ]
    }

@app.get("/api/compare")
def compare_tickers(tickers: str = "NVDA,AMD,INTC"):
    """Side-by-side comparison of 2 to 4 tickers."""
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()][:4]
    results = []
    for t in ticker_list:
        try:
            report = engine.analyze_ticker(t)
            forensics = report.get("forensics", {})
            mkt = report.get("market_data", {})
            solv = report.get("solvency_liquidity", {})
            results.append({
                "ticker": t,
                "name": mkt.get("name", t),
                "price": mkt.get("current_price", 0.0),
                "market_cap": mkt.get("market_cap", 0),
                "pe": mkt.get("trailing_pe"),
                "risk_score": report.get("risk_score", 0),
                "beneish": forensics.get("beneish_m_score", {}),
                "altman": forensics.get("altman_z_score", {}),
                "piotroski": forensics.get("piotroski_f_score", {}),
                "montier": forensics.get("montier_c_score", {}),
                "solvency": solv,
                "anomalies_count": len(forensics.get("anomalies", [])),
                "valuation": report.get("valuation_model", {})
            })
        except Exception as e:
            logger.error(f"Error comparing {t}: {e}")
    return {"tickers": ticker_list, "comparison": results}

@app.get("/api/export-csv/{ticker}")
def export_csv(ticker: str):
    """Generates clean CSV spreadsheet export of audited financials."""
    try:
        report = engine.analyze_ticker(ticker)
        fin_series = report.get("financial_series", [])
        if not fin_series:
            raise HTTPException(status_code=404, detail="No financial series available")

        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        years = [f"FY {item.get('fiscal_year', '')}" for item in fin_series]
        writer.writerow(["Line Item (USD)"] + years)

        fields = [
            ("Revenue", "revenue"),
            ("Gross Profit", "gross_profit"),
            ("Operating Income (EBIT)", "operating_income"),
            ("Net Income", "net_income"),
            ("Operating Cash Flow (CFO)", "operating_cash_flow"),
            ("Total Assets", "total_assets"),
            ("Accounts Receivable", "accounts_receivable"),
            ("Inventories", "inventory"),
            ("Total Liabilities", "total_liabilities"),
            ("Long-Term Debt", "long_term_debt")
        ]

        for label, key in fields:
            row = [label] + [item.get(key, "") for item in fin_series]
            writer.writerow(row)

        output.seek(0)
        headers = {
            "Content-Disposition": f"attachment; filename={ticker.upper()}_FINANCIALS.csv"
        }
        return Response(content=output.getvalue(), media_type="text/csv", headers=headers)
    except Exception as e:
        logger.error(f"Error generating CSV for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dossier/{ticker}")
def get_dossier(ticker: str):
    """Generate institutional markdown forensic due diligence dossier."""
    try:
        md_content = engine.generate_dossier_markdown(ticker)
        headers = {
            "Content-Disposition": f"attachment; filename={ticker.upper()}_FORENSIC_DOSSIER.md"
        }
        return Response(content=md_content, media_type="text/markdown", headers=headers)
    except Exception as e:
        logger.error(f"Error generating dossier for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/screen")
def screen_watchlist(preset: str = "mega_tech", tickers: Optional[str] = None):
    """Run batch screener across watchlists."""
    try:
        ticker_list = []
        if tickers:
            ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
        elif preset in PRESET_WATCHLISTS:
            ticker_list = PRESET_WATCHLISTS[preset]
        else:
            ticker_list = PRESET_WATCHLISTS["mega_tech"]

        results = screener.screen_tickers(ticker_list)
        return {"preset": preset, "count": len(results), "results": results}
    except Exception as e:
        logger.error(f"Error screening: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "ONLINE", "engine": "VETTR Core v1.0", "sec_edgar": "CONNECTED"}
