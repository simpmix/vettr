import logging
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from argus.engine import ArgusEngine
from argus.market.provider import MarketDataProvider
from argus.screener import ArgusScreener, PRESET_WATCHLISTS
from argus.data.tickers import search_securities
from argus.config import SERVER_HOST, SERVER_PORT

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ARGUS Financial Forensics Terminal",
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

engine = ArgusEngine()
screener = ArgusScreener()
STATIC_DIR = Path(__file__).resolve().parent / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "ARGUS Terminal API online. Static frontend not found."}

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

@app.get("/api/candles/{ticker}")
def get_candles(ticker: str, period: str = "1y", interval: str = "1d"):
    """Fetch OHLCV historical candlestick data."""
    try:
        candles = MarketDataProvider.get_historical_candles(ticker, period=period, interval=interval)
        return {"ticker": ticker.upper(), "candles": candles}
    except Exception as e:
        logger.error(f"Error fetching candles for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "ONLINE", "engine": "ARGUS Core v1.0", "sec_edgar": "CONNECTED"}
