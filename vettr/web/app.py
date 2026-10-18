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
from vettr.market.provider import MarketDataProvider
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
