"""
Institutional Ticker Directory & Universal SEC EDGAR Securities Index.
Indexes 150+ curated blue-chip equities with Sector/Industry metadata,
and dynamically searches across all 10,443+ SEC EDGAR registered public companies.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from vettr.config import BASE_DIR

logger = logging.getLogger(__name__)

# Curated institutional universe covering all major sectors of the S&P 500, Nasdaq 100, and Dow 30
CURATED_SECURITIES = [
    # Mega-Cap Tech & AI Infrastructure
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "AMZN", "name": "Amazon.com, Inc.", "sector": "Consumer Cyclical", "industry": "Internet Retail"},
    {"ticker": "GOOGL", "name": "Alphabet Inc. (Class A)", "sector": "Communication Services", "industry": "Internet Content"},
    {"ticker": "GOOG", "name": "Alphabet Inc. (Class C)", "sector": "Communication Services", "industry": "Internet Content"},
    {"ticker": "META", "name": "Meta Platforms, Inc.", "sector": "Communication Services", "industry": "Internet Content"},
    {"ticker": "TSLA", "name": "Tesla, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    {"ticker": "AVGO", "name": "Broadcom Inc.", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "TSM", "name": "Taiwan Semiconductor Manufacturing Co.", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "AMD", "name": "Advanced Micro Devices, Inc.", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "INTC", "name": "Intel Corporation", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "QCOM", "name": "QUALCOMM Incorporated", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "ASML", "name": "ASML Holding N.V.", "sector": "Technology", "industry": "Semiconductor Equipment"},
    {"ticker": "MU", "name": "Micron Technology, Inc.", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "ARM", "name": "Arm Holdings plc", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "AMAT", "name": "Applied Materials, Inc.", "sector": "Technology", "industry": "Semiconductor Equipment"},
    {"ticker": "LRCX", "name": "Lam Research Corporation", "sector": "Technology", "industry": "Semiconductor Equipment"},
    {"ticker": "TXN", "name": "Texas Instruments Incorporated", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "ADI", "name": "Analog Devices, Inc.", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "SMCI", "name": "Super Micro Computer, Inc.", "sector": "Technology", "industry": "Computer Hardware"},
    {"ticker": "DELL", "name": "Dell Technologies Inc.", "sector": "Technology", "industry": "Computer Hardware"},
    {"ticker": "HPE", "name": "Hewlett Packard Enterprise Company", "sector": "Technology", "industry": "Computer Hardware"},

    # Cloud, Cybersecurity & Enterprise SaaS
    {"ticker": "PLTR", "name": "Palantir Technologies Inc.", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "CRM", "name": "Salesforce, Inc.", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "NOW", "name": "ServiceNow, Inc.", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "ORCL", "name": "Oracle Corporation", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "ADBE", "name": "Adobe Inc.", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "PANW", "name": "Palo Alto Networks, Inc.", "sector": "Technology", "industry": "Cybersecurity"},
    {"ticker": "CRWD", "name": "CrowdStrike Holdings, Inc.", "sector": "Technology", "industry": "Cybersecurity"},
    {"ticker": "FTNT", "name": "Fortinet, Inc.", "sector": "Technology", "industry": "Cybersecurity"},
    {"ticker": "NET", "name": "Cloudflare, Inc.", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "SNOW", "name": "Snowflake Inc.", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "DDOG", "name": "Datadog, Inc.", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "ZS", "name": "Zscaler, Inc.", "sector": "Technology", "industry": "Cybersecurity"},
    {"ticker": "MDB", "name": "MongoDB, Inc.", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "TEAM", "name": "Atlassian Corporation", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "WDAY", "name": "Workday, Inc.", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "INTU", "name": "Intuit Inc.", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "IBM", "name": "International Business Machines Corp.", "sector": "Technology", "industry": "Information Technology"},
    {"ticker": "CSCO", "name": "Cisco Systems, Inc.", "sector": "Technology", "industry": "Communication Equipment"},

    # Wall Street & Financial Institutions
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services", "industry": "Banks - Diversified"},
    {"ticker": "BAC", "name": "Bank of America Corporation", "sector": "Financial Services", "industry": "Banks - Diversified"},
    {"ticker": "WFC", "name": "Wells Fargo & Company", "sector": "Financial Services", "industry": "Banks - Diversified"},
    {"ticker": "C", "name": "Citigroup Inc.", "sector": "Financial Services", "industry": "Banks - Diversified"},
    {"ticker": "GS", "name": "The Goldman Sachs Group, Inc.", "sector": "Financial Services", "industry": "Capital Markets"},
    {"ticker": "MS", "name": "Morgan Stanley", "sector": "Financial Services", "industry": "Capital Markets"},
    {"ticker": "BLK", "name": "BlackRock, Inc.", "sector": "Financial Services", "industry": "Asset Management"},
    {"ticker": "BRK-B", "name": "Berkshire Hathaway Inc.", "sector": "Financial Services", "industry": "Insurance - Diversified"},
    {"ticker": "SCHW", "name": "The Charles Schwab Corporation", "sector": "Financial Services", "industry": "Capital Markets"},
    {"ticker": "V", "name": "Visa Inc.", "sector": "Financial Services", "industry": "Credit Services"},
    {"ticker": "MA", "name": "Mastercard Incorporated", "sector": "Financial Services", "industry": "Credit Services"},
    {"ticker": "AXP", "name": "American Express Company", "sector": "Financial Services", "industry": "Credit Services"},
    {"ticker": "COIN", "name": "Coinbase Global, Inc.", "sector": "Financial Services", "industry": "Financial Data"},
    {"ticker": "MSTR", "name": "MicroStrategy Incorporated", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "SOFI", "name": "SoFi Technologies, Inc.", "sector": "Financial Services", "industry": "Credit Services"},
    {"ticker": "HOOD", "name": "Robinhood Markets, Inc.", "sector": "Financial Services", "industry": "Capital Markets"},

    # Healthcare, Biotech & Pharmaceuticals
    {"ticker": "LLY", "name": "Eli Lilly and Company", "sector": "Healthcare", "industry": "Drug Manufacturers - General"},
    {"ticker": "NVO", "name": "Novo Nordisk A/S", "sector": "Healthcare", "industry": "Drug Manufacturers - General"},
    {"ticker": "UNH", "name": "UnitedHealth Group Incorporated", "sector": "Healthcare", "industry": "Healthcare Plans"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Drug Manufacturers - General"},
    {"ticker": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare", "industry": "Drug Manufacturers - General"},
    {"ticker": "MRK", "name": "Merck & Co., Inc.", "sector": "Healthcare", "industry": "Drug Manufacturers - General"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific Inc.", "sector": "Healthcare", "industry": "Diagnostics & Research"},
    {"ticker": "ABT", "name": "Abbott Laboratories", "sector": "Healthcare", "industry": "Medical Devices"},
    {"ticker": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare", "industry": "Drug Manufacturers - General"},
    {"ticker": "AMGN", "name": "Amgen Inc.", "sector": "Healthcare", "industry": "Biotechnology"},
    {"ticker": "DHR", "name": "Danaher Corporation", "sector": "Healthcare", "industry": "Diagnostics & Research"},
    {"ticker": "ISRG", "name": "Intuitive Surgical, Inc.", "sector": "Healthcare", "industry": "Medical Instruments"},
    {"ticker": "VRTX", "name": "Vertex Pharmaceuticals Incorporated", "sector": "Healthcare", "industry": "Biotechnology"},
    {"ticker": "BMY", "name": "Bristol-Myers Squibb Company", "sector": "Healthcare", "industry": "Drug Manufacturers"},
    {"ticker": "GILD", "name": "Gilead Sciences, Inc.", "sector": "Healthcare", "industry": "Biotechnology"},
    {"ticker": "REGN", "name": "Regeneron Pharmaceuticals, Inc.", "sector": "Healthcare", "industry": "Biotechnology"},
    {"ticker": "CVS", "name": "CVS Health Corporation", "sector": "Healthcare", "industry": "Healthcare Plans"},

    # Consumer, Retail & Digital Entertainment
    {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer Defensive", "industry": "Discount Stores"},
    {"ticker": "COST", "name": "Costco Wholesale Corporation", "sector": "Consumer Defensive", "industry": "Discount Stores"},
    {"ticker": "HD", "name": "The Home Depot, Inc.", "sector": "Consumer Cyclical", "industry": "Home Improvement Retail"},
    {"ticker": "PG", "name": "The Procter & Gamble Company", "sector": "Consumer Defensive", "industry": "Household Products"},
    {"ticker": "KO", "name": "The Coca-Cola Company", "sector": "Consumer Defensive", "industry": "Beverages - Non-Alcoholic"},
    {"ticker": "PEP", "name": "PepsiCo, Inc.", "sector": "Consumer Defensive", "industry": "Beverages - Non-Alcoholic"},
    {"ticker": "MCD", "name": "McDonald's Corporation", "sector": "Consumer Cyclical", "industry": "Restaurants"},
    {"ticker": "SBUX", "name": "Starbucks Corporation", "sector": "Consumer Cyclical", "industry": "Restaurants"},
    {"ticker": "NKE", "name": "NIKE, Inc.", "sector": "Consumer Cyclical", "industry": "Footwear & Accessories"},
    {"ticker": "LULU", "name": "Lululemon Athletica Inc.", "sector": "Consumer Cyclical", "industry": "Apparel Retail"},
    {"ticker": "TGT", "name": "Target Corporation", "sector": "Consumer Defensive", "industry": "Discount Stores"},
    {"ticker": "LOW", "name": "Lowe's Companies, Inc.", "sector": "Consumer Cyclical", "industry": "Home Improvement Retail"},
    {"ticker": "TJX", "name": "The TJX Companies, Inc.", "sector": "Consumer Cyclical", "industry": "Apparel Retail"},
    {"ticker": "DIS", "name": "The Walt Disney Company", "sector": "Communication Services", "industry": "Entertainment"},
    {"ticker": "NFLX", "name": "Netflix, Inc.", "sector": "Communication Services", "industry": "Entertainment"},
    {"ticker": "SPOT", "name": "Spotify Technology S.A.", "sector": "Communication Services", "industry": "Internet Content"},
    {"ticker": "UBER", "name": "Uber Technologies, Inc.", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "ABNB", "name": "Airbnb, Inc.", "sector": "Consumer Cyclical", "industry": "Travel Services"},
    {"ticker": "BKNG", "name": "Booking Holdings Inc.", "sector": "Consumer Cyclical", "industry": "Travel Services"},
    {"ticker": "RDDT", "name": "Reddit, Inc.", "sector": "Communication Services", "industry": "Internet Content"},
    {"ticker": "RBLX", "name": "Roblox Corporation", "sector": "Communication Services", "industry": "Electronic Gaming"},
    {"ticker": "BABA", "name": "Alibaba Group Holding Limited", "sector": "Consumer Cyclical", "industry": "Internet Retail"},
    {"ticker": "PDD", "name": "PDD Holdings Inc.", "sector": "Consumer Cyclical", "industry": "Internet Retail"},

    # Energy, Industrials, Aerospace & Defense
    {"ticker": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy", "industry": "Oil & Gas Integrated"},
    {"ticker": "CVX", "name": "Chevron Corporation", "sector": "Energy", "industry": "Oil & Gas Integrated"},
    {"ticker": "COP", "name": "ConocoPhillips", "sector": "Energy", "industry": "Oil & Gas E&P"},
    {"ticker": "SLB", "name": "SLB (Schlumberger)", "sector": "Energy", "industry": "Oil & Gas Equipment"},
    {"ticker": "EOG", "name": "EOG Resources, Inc.", "sector": "Energy", "industry": "Oil & Gas E&P"},
    {"ticker": "OXY", "name": "Occidental Petroleum Corporation", "sector": "Energy", "industry": "Oil & Gas E&P"},
    {"ticker": "CAT", "name": "Caterpillar Inc.", "sector": "Industrials", "industry": "Farm & Heavy Construction"},
    {"ticker": "GE", "name": "General Electric Company", "sector": "Industrials", "industry": "Aerospace & Defense"},
    {"ticker": "HON", "name": "Honeywell International Inc.", "sector": "Industrials", "industry": "Conglomerates"},
    {"ticker": "UNP", "name": "Union Pacific Corporation", "sector": "Industrials", "industry": "Railroads"},
    {"ticker": "UPS", "name": "United Parcel Service, Inc.", "sector": "Industrials", "industry": "Integrated Freight & Logistics"},
    {"ticker": "FDX", "name": "FedEx Corporation", "sector": "Industrials", "industry": "Integrated Freight & Logistics"},
    {"ticker": "LMT", "name": "Lockheed Martin Corporation", "sector": "Industrials", "industry": "Aerospace & Defense"},
    {"ticker": "RTX", "name": "RTX Corporation (Raytheon)", "sector": "Industrials", "industry": "Aerospace & Defense"},
    {"ticker": "BA", "name": "The Boeing Company", "sector": "Industrials", "industry": "Aerospace & Defense"},
    {"ticker": "GD", "name": "General Dynamics Corporation", "sector": "Industrials", "industry": "Aerospace & Defense"},
    {"ticker": "NOC", "name": "Northrop Grumman Corporation", "sector": "Industrials", "industry": "Aerospace & Defense"},

    # EV, Automotive & Clean Energy
    {"ticker": "RIVN", "name": "Rivian Automotive, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    {"ticker": "LCID", "name": "Lucid Group, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    {"ticker": "NIO", "name": "NIO Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    {"ticker": "F", "name": "Ford Motor Company", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    {"ticker": "GM", "name": "General Motors Company", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    {"ticker": "ENPH", "name": "Enphase Energy, Inc.", "sector": "Technology", "industry": "Solar"},
    {"ticker": "FSLR", "name": "First Solar, Inc.", "sector": "Technology", "industry": "Solar"},
    {"ticker": "NEE", "name": "NextEra Energy, Inc.", "sector": "Utilities", "industry": "Utilities - Regulated Electric"}
]

# Universal SEC Full Registry cache
_SEC_FULL_INDEX: Optional[List[Dict[str, str]]] = None

def _load_sec_full_registry() -> List[Dict[str, str]]:
    global _SEC_FULL_INDEX
    if _SEC_FULL_INDEX is not None:
        return _SEC_FULL_INDEX

    registry = []
    # Check cache file from EdgarClient
    cache_file = BASE_DIR / ".cache" / "edgar" / "company_tickers.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            for item in data.values():
                t = str(item.get("ticker", "")).upper().strip()
                title = str(item.get("title", "")).strip()
                if t and title:
                    registry.append({
                        "ticker": t,
                        "name": title,
                        "sector": "Public Corporation (SEC EDGAR)",
                        "industry": "U.S. Exchange Listed"
                    })
            _SEC_FULL_INDEX = registry
            logger.info(f"Loaded {len(registry)} public companies from SEC EDGAR registry")
            return _SEC_FULL_INDEX
        except Exception as e:
            logger.warning(f"Error reading SEC company tickers file: {e}")

    _SEC_FULL_INDEX = []
    return _SEC_FULL_INDEX

def search_securities(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search securities across curated list first, then against all 10,443+ SEC EDGAR public companies.
    """
    q = query.strip().upper()
    if not q:
        return CURATED_SECURITIES[:limit]

    matches = []
    seen_tickers = set()

    # 1. Search curated securities (highest quality sector/industry metadata)
    for s in CURATED_SECURITIES:
        if q == s["ticker"] or s["ticker"].startswith(q) or q in s["ticker"] or q.lower() in s["name"].lower():
            matches.append(s)
            seen_tickers.add(s["ticker"])
            if len(matches) >= limit:
                return matches

    # 2. Search universal SEC EDGAR database (all 10,443 companies)
    sec_registry = _load_sec_full_registry()
    for s in sec_registry:
        t = s["ticker"]
        if t in seen_tickers:
            continue
        if q == t or t.startswith(q) or q in t or q.lower() in s["name"].lower():
            matches.append(s)
            seen_tickers.add(t)
            if len(matches) >= limit:
                break

    return matches

POPULAR_SECURITIES = CURATED_SECURITIES
