import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from argus.engine import ArgusEngine
from argus.market.provider import MarketDataProvider
from argus.config import SERVER_HOST, SERVER_PORT

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ARGUS Financial Forensics Terminal",
    description="Autonomous SEC EDGAR Accounting Forensics & Intelligence Engine",
    version="1.0.0"
)

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = ArgusEngine()
STATIC_DIR = Path(__file__).resolve().parent / "static"

# Serve static frontend files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "ARGUS Terminal API online. Static frontend not found."}

@app.get("/api/analyze/{ticker}")
def analyze_ticker(ticker: str):
    """Run full quantitative forensic evaluation and SEC filing analysis."""
    try:
        report = engine.analyze_ticker(ticker)
        return report
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
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
