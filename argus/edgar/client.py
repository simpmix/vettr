import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from argus.config import CACHE_DIR, SEC_HEADERS, SEC_WWW_HEADERS

logger = logging.getLogger(__name__)

class EdgarClient:
    """
    Direct SEC EDGAR client supporting:
    - Ticker to CIK resolution
    - Company submissions (filing history: 10-K, 10-Q, 8-K, Form 4)
    - XBRL standardized company facts (GAAP financials)
    - Filing document retrieval
    """

    TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
    SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
    COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{filename}"

    def __init__(self, cache_ttl_hours: int = 24):
        self.cache_dir = CACHE_DIR / "edgar"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = cache_ttl_hours * 3600
        self._ticker_map: Optional[Dict[str, Dict[str, Any]]] = None
        self._last_request_time = 0.0

    def _rate_limit(self):
        """SEC enforces a strict rate limit of max 10 requests per second."""
        elapsed = time.time() - self._last_request_time
        if elapsed < 0.12:  # ~8 req/sec max to stay safely under limit
            time.sleep(0.12 - elapsed)
        self._last_request_time = time.time()

    def _get(self, url: str, is_data_host: bool = True) -> requests.Response:
        self._rate_limit()
        headers = SEC_HEADERS if is_data_host else SEC_WWW_HEADERS
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp

    def get_ticker_map(self) -> Dict[str, Dict[str, Any]]:
        """Returns map of TICKER -> {cik: str, title: str, ticker: str}."""
        if self._ticker_map:
            return self._ticker_map

        cache_file = self.cache_dir / "company_tickers.json"
        if cache_file.exists() and (time.time() - cache_file.stat().st_mtime < self.cache_ttl):
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                self._ticker_map = {v["ticker"].upper(): v for v in data.values()}
                return self._ticker_map
            except Exception as e:
                logger.warning(f"Error loading cached tickers: {e}")

        try:
            resp = self._get(self.TICKERS_URL, is_data_host=False)
            data = resp.json()
            cache_file.write_text(json.dumps(data), encoding="utf-8")
            self._ticker_map = {v["ticker"].upper(): v for v in data.values()}
            return self._ticker_map
        except Exception as e:
            logger.error(f"Failed to fetch SEC tickers: {e}")
            return {}

    def get_cik_for_ticker(self, ticker: str) -> Optional[str]:
        t_map = self.get_ticker_map()
        clean_ticker = ticker.strip().upper()
        if clean_ticker in t_map:
            # Format to 10 digits as required by SEC API
            return str(t_map[clean_ticker]["cik_str"]).zfill(10)
        return None

    def get_company_submissions(self, cik: str) -> Dict[str, Any]:
        """Fetch all recent filings for a given CIK."""
        clean_cik = cik.zfill(10)
        cache_file = self.cache_dir / f"submissions_{clean_cik}.json"
        
        # 6 hours cache for submissions
        if cache_file.exists() and (time.time() - cache_file.stat().st_mtime < 21600):
            try:
                return json.loads(cache_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        url = self.SUBMISSIONS_URL.format(cik=clean_cik)
        resp = self._get(url, is_data_host=True)
        data = resp.json()
        cache_file.write_text(json.dumps(data), encoding="utf-8")
        return data

    def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """Fetch standardized US-GAAP XBRL financial facts."""
        clean_cik = cik.zfill(10)
        cache_file = self.cache_dir / f"facts_{clean_cik}.json"

        # 12 hours cache for financial facts
        if cache_file.exists() and (time.time() - cache_file.stat().st_mtime < 43200):
            try:
                return json.loads(cache_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        url = self.COMPANY_FACTS_URL.format(cik=clean_cik)
        resp = self._get(url, is_data_host=True)
        data = resp.json()
        cache_file.write_text(json.dumps(data), encoding="utf-8")
        return data

    def get_filing_list(self, cik: str, form_types: Optional[List[str]] = None, limit: int = 25) -> List[Dict[str, Any]]:
        """Parses recent filings table from submissions into structured list."""
        submissions = self.get_company_submissions(cik)
        recent = submissions.get("filings", {}).get("recent", {})
        if not recent or "form" not in recent:
            return []

        forms = recent["form"]
        accession_nums = recent["accessionNumber"]
        filing_dates = recent["filingDate"]
        report_dates = recent["reportDate"]
        primary_docs = recent["primaryDocument"]
        doc_descriptions = recent.get("primaryDocDescription", [""] * len(forms))

        results = []
        for i in range(len(forms)):
            form = forms[i]
            if form_types and form not in form_types:
                continue

            acc_raw = accession_nums[i]
            acc_clean = acc_raw.replace("-", "")
            cik_int = str(int(cik))

            url = self.ARCHIVE_URL.format(
                cik=cik_int,
                accession=acc_clean,
                filename=primary_docs[i]
            )

            results.append({
                "form": form,
                "filing_date": filing_dates[i],
                "report_date": report_dates[i] if i < len(report_dates) else filing_dates[i],
                "accession_number": acc_raw,
                "primary_document": primary_docs[i],
                "description": doc_descriptions[i] if i < len(doc_descriptions) else "",
                "url": url
            })

            if len(results) >= limit:
                break

        return results

    def fetch_filing_content(self, url: str) -> str:
        """Download raw filing text/html, cached on disk."""
        filename = re.sub(r"[^a-zA-Z0-9_\.]", "_", url.split("/")[-1])
        cache_file = self.cache_dir / f"doc_{filename}"
        if cache_file.exists():
            return cache_file.read_text(encoding="utf-8", errors="ignore")

        resp = self._get(url, is_data_host=False)
        text = resp.text
        cache_file.write_text(text, encoding="utf-8", errors="ignore")
        return text
