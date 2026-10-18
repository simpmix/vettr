import datetime
import logging
import time
from typing import Any, Dict, List, Optional
import yfinance as yf

logger = logging.getLogger(__name__)

INDEX_SYMBOLS = [
    {"symbol": "SPY", "name": "S&P 500"},
    {"symbol": "QQQ", "name": "NASDAQ 100"},
    {"symbol": "DIA", "name": "DOW 30"},
    {"symbol": "IWM", "name": "RUSSELL 2000"},
    {"symbol": "^VIX", "name": "VIX VOLATILITY"}
]

ACTIVE_LEADERS = ["NVDA", "AAPL", "MSFT", "TSLA", "AMD", "AMZN", "META", "GOOGL", "PLTR", "MSTR"]

class ExchangePulseTracker:
    """
    Continuous Stock Exchange Telemetry & Market Pulse Engine.
    Tracks major equity indices and active market leaders with live price updates.
    """

    _cache_data: Optional[Dict[str, Any]] = None
    _last_fetch_time: float = 0.0
    _cache_ttl_seconds: int = 15

    @classmethod
    def get_market_status(cls) -> str:
        """Determines if US Stock Exchanges (NYSE/NASDAQ) are OPEN, PRE-MARKET, AFTER-HOURS, or CLOSED."""
        # NYSE hours: Monday to Friday 9:30 AM to 4:00 PM Eastern Time (UTC-4 / UTC-5)
        # Using UTC for standardized calculation
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        weekday = now_utc.weekday()  # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday

        if weekday >= 5:
            return "EXCHANGES CLOSED (WEEKEND)"

        # Approximate Eastern Time: UTC - 4 (EDT) / UTC - 5 (EST)
        # 9:30 AM ET = 13:30 or 14:30 UTC
        hour_utc = now_utc.hour + (now_utc.minute / 60.0)
        
        # 13:30 UTC to 20:00 UTC covers regular trading
        if 13.5 <= hour_utc < 20.0:
            return "EXCHANGES LIVE (REGULAR HOURS)"
        elif 8.0 <= hour_utc < 13.5:
            return "EXCHANGES PRE-MARKET"
        elif 20.0 <= hour_utc < 24.0:
            return "EXCHANGES AFTER-HOURS"
        else:
            return "EXCHANGES CLOSED"

    @classmethod
    def get_exchange_pulse(cls) -> Dict[str, Any]:
        """Fetches live quotes for indices and market leaders with 15-second caching."""
        now = time.time()
        if cls._cache_data and (now - cls._last_fetch_time < cls._cache_ttl_seconds):
            return cls._cache_data

        all_tickers = [item["symbol"] for item in INDEX_SYMBOLS] + ACTIVE_LEADERS
        ticker_str = " ".join(all_tickers)

        indices_data = []
        leaders_data = []

        try:
            tickers_obj = yf.Tickers(ticker_str)
            
            # 1. Process Index symbols
            for idx_info in INDEX_SYMBOLS:
                sym = idx_info["symbol"]
                t = tickers_obj.tickers.get(sym)
                price = 0.0
                prev_close = 0.0
                change = 0.0
                change_pct = 0.0

                if t:
                    try:
                        price = float(t.fast_info.last_price or 0.0)
                        prev_close = float(t.fast_info.previous_close or price)
                    except Exception:
                        price = 0.0
                        prev_close = 0.0

                if price > 0 and prev_close > 0:
                    change = price - prev_close
                    change_pct = (change / prev_close) * 100

                indices_data.append({
                    "symbol": sym,
                    "name": idx_info["name"],
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2)
                })

            # 2. Process Active Leaders
            for sym in ACTIVE_LEADERS:
                t = tickers_obj.tickers.get(sym)
                price = 0.0
                prev_close = 0.0
                change = 0.0
                change_pct = 0.0

                if t:
                    try:
                        price = float(t.fast_info.last_price or 0.0)
                        prev_close = float(t.fast_info.previous_close or price)
                    except Exception:
                        price = 0.0
                        prev_close = 0.0

                if price > 0 and prev_close > 0:
                    change = price - prev_close
                    change_pct = (change / prev_close) * 100

                leaders_data.append({
                    "symbol": sym,
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2)
                })

            cls._cache_data = {
                "market_status": cls.get_market_status(),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "indices": indices_data,
                "leaders": leaders_data
            }
            cls._last_fetch_time = now
            return cls._cache_data

        except Exception as e:
            logger.error(f"Error updating exchange pulse: {e}")
            if cls._cache_data:
                return cls._cache_data
            return {
                "market_status": cls.get_market_status(),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "indices": [],
                "leaders": [],
                "error": str(e)
            }
