import logging
from typing import Any, Dict, List, Optional
import yfinance as yf

logger = logging.getLogger(__name__)

class MarketDataProvider:
    """
    Market data provider via yfinance:
    - Real-time quote, market valuation multiples
    - Historical price candles for charting
    - Company profile & sector data
    """

    @classmethod
    def get_market_overview(cls, ticker: str) -> Dict[str, Any]:
        """Fetches live quotes, valuation metrics, and business info."""
        clean_ticker = ticker.strip().upper()
        try:
            t = yf.Ticker(clean_ticker)
            info = t.info or {}

            current_price = (
                info.get("currentPrice")
                or info.get("regularMarketPrice")
                or info.get("previousClose")
                or 0.0
            )
            prev_close = info.get("previousClose") or current_price
            price_change = current_price - prev_close if prev_close else 0.0
            price_change_pct = (price_change / prev_close * 100) if prev_close else 0.0

            return {
                "ticker": clean_ticker,
                "name": info.get("shortName") or info.get("longName") or clean_ticker,
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "summary": info.get("longBusinessSummary", ""),
                "website": info.get("website", ""),
                "current_price": round(current_price, 2),
                "previous_close": round(prev_close, 2),
                "change": round(price_change, 2),
                "change_pct": round(price_change_pct, 2),
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "trailing_pe": round(info.get("trailingPE", 0.0), 2) if info.get("trailingPE") else None,
                "forward_pe": round(info.get("forwardPE", 0.0), 2) if info.get("forwardPE") else None,
                "price_to_sales": round(info.get("priceToSalesTrailing12Months", 0.0), 2) if info.get("priceToSalesTrailing12Months") else None,
                "ev_to_ebitda": round(info.get("enterpriseToEbitda", 0.0), 2) if info.get("enterpriseToEbitda") else None,
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                "target_mean_price": info.get("targetMeanPrice"),
                "recommendation_key": info.get("recommendationKey", "N/A").upper(),
                "currency": info.get("currency", "USD")
            }
        except Exception as e:
            logger.error(f"Error fetching market overview for {clean_ticker}: {e}")
            return {
                "ticker": clean_ticker,
                "name": clean_ticker,
                "current_price": 0.0,
                "market_cap": None,
                "error": str(e)
            }

    @classmethod
    def get_historical_candles(cls, ticker: str, period: str = "1y", interval: str = "1d") -> List[Dict[str, Any]]:
        """Fetches historical OHLCV data for charts."""
        clean_ticker = ticker.strip().upper()
        try:
            t = yf.Ticker(clean_ticker)
            df = t.history(period=period, interval=interval)
            if df.empty:
                return []

            candles = []
            for index, row in df.iterrows():
                date_str = index.strftime("%Y-%m-%d")
                candles.append({
                    "date": date_str,
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"])
                })
            return candles
        except Exception as e:
            logger.error(f"Error fetching candles for {clean_ticker}: {e}")
            return []
