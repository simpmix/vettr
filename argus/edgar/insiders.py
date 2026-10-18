import logging
import re
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from argus.edgar.client import EdgarClient

logger = logging.getLogger(__name__)

class InsiderScanner:
    """
    Parses US SEC Form 4 (Statement of Changes in Beneficial Ownership).
    Tracks C-suite & Director buying/selling activity, net volume, and transaction types.
    """

    def __init__(self, edgar_client: Optional[EdgarClient] = None):
        self.edgar = edgar_client or EdgarClient()

    def get_recent_insider_trades(self, cik: str, limit: int = 15) -> Dict[str, Any]:
        """
        Fetches and extracts Form 4 filings for a company.
        Calculates Net Buy/Sell volume and clusters.
        """
        form4_filings = self.edgar.get_filing_list(cik, form_types=["4"], limit=limit)
        if not form4_filings:
            return {
                "trades": [],
                "net_volume_usd": 0.0,
                "total_buys_usd": 0.0,
                "total_sells_usd": 0.0,
                "sentiment": "NEUTRAL"
            }

        trades = []
        total_buys = 0.0
        total_sells = 0.0

        for f in form4_filings[:10]:
            try:
                content = self.edgar.fetch_filing_content(f["url"])
                parsed_trade = self._parse_form4_document(content, f)
                if parsed_trade:
                    trades.append(parsed_trade)
                    if parsed_trade.get("transaction_type") == "BUY":
                        total_buys += parsed_trade.get("total_value", 0.0)
                    elif parsed_trade.get("transaction_type") == "SELL":
                        total_sells += parsed_trade.get("total_value", 0.0)
            except Exception as e:
                logger.debug(f"Could not parse Form 4 {f.get('accession_number')}: {e}")

        net_volume = total_buys - total_sells

        if total_sells > 10_000_000 and total_buys == 0:
            sentiment = "HEAVY INSIDER SELLING"
        elif total_buys > total_sells and total_buys > 500_000:
            sentiment = "BULLISH INSIDER ACCUMULATION"
        elif total_sells > 0:
            sentiment = "MODERATE INSIDER PROFIT-TAKING"
        else:
            sentiment = "NEUTRAL / NO DIRECT TRADES"

        return {
            "trades": trades,
            "net_volume_usd": round(net_volume, 2),
            "total_buys_usd": round(total_buys, 2),
            "total_sells_usd": round(total_sells, 2),
            "sentiment": sentiment
        }

    def _parse_form4_document(self, xml_or_html: str, meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parses individual Form 4 to extract reporting owner, title, shares, and price."""
        # Try finding reporting owner name and relationship
        soup = BeautifulSoup(xml_or_html, "lxml")
        
        owner_name = "Insider / Officer"
        title = "Director / 10% Owner"
        is_officer = False
        is_director = False

        # Attempt XML tag search or fallback text patterns
        rpt_owner = soup.find("rptownername") or soup.find("rptowner")
        if rpt_owner:
            owner_name = rpt_owner.get_text().strip()

        officer_title = soup.find("officertitle")
        if officer_title:
            title = officer_title.get_text().strip()

        # Check transaction code (P = Open Market Purchase, S = Open Market Sale, M = Exercise)
        trans_code = "S"
        code_tag = soup.find("transactioncode")
        if code_tag:
            trans_code = code_tag.get_text().strip().upper()

        shares = 0.0
        shares_tag = soup.find("transactionshares")
        if shares_tag:
            val_tag = shares_tag.find("value")
            if val_tag:
                try:
                    shares = float(val_tag.get_text().strip())
                except ValueError:
                    pass

        price = 0.0
        price_tag = soup.find("transactionpricepershare")
        if price_tag:
            val_tag = price_tag.find("value")
            if val_tag:
                try:
                    price = float(val_tag.get_text().strip())
                except ValueError:
                    pass

        # If values parsed
        total_val = shares * price if (shares and price) else 0.0
        tx_type = "BUY" if trans_code == "P" else ("SELL" if trans_code == "S" else "OPTION/AWARD")

        return {
            "owner": owner_name,
            "title": title,
            "transaction_date": meta.get("filing_date", ""),
            "transaction_type": tx_type,
            "shares": int(shares),
            "price_per_share": round(price, 2),
            "total_value": round(total_val, 2),
            "filing_url": meta.get("url", "")
        }
