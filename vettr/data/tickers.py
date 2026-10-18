"""
Institutional ticker directory and pre-indexed securities database
"""

POPULAR_SECURITIES = [
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "industry": "Internet Retail"},
    {"ticker": "GOOGL", "name": "Alphabet Inc. (Google)", "sector": "Communication Services", "industry": "Internet Content"},
    {"ticker": "META", "name": "Meta Platforms Inc.", "sector": "Communication Services", "industry": "Internet Content"},
    {"ticker": "TSLA", "name": "Tesla, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    {"ticker": "AVGO", "name": "Broadcom Inc.", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "TSM", "name": "Taiwan Semiconductor Manufacturing", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "AMD", "name": "Advanced Micro Devices, Inc.", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "INTC", "name": "Intel Corporation", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "QCOM", "name": "QUALCOMM Incorporated", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "ASML", "name": "ASML Holding N.V.", "sector": "Technology", "industry": "Semiconductor Equipment"},
    {"ticker": "PLTR", "name": "Palantir Technologies Inc.", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "SNOW", "name": "Snowflake Inc.", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "CRWD", "name": "CrowdStrike Holdings, Inc.", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "PANW", "name": "Palo Alto Networks, Inc.", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "NET", "name": "Cloudflare, Inc.", "sector": "Technology", "industry": "Software - Cloud"},
    {"ticker": "DDOG", "name": "Datadog, Inc.", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "CRM", "name": "Salesforce, Inc.", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "ORCL", "name": "Oracle Corporation", "sector": "Technology", "industry": "Software - Infrastructure"},
    {"ticker": "IBM", "name": "International Business Machines", "sector": "Technology", "industry": "Information Technology"},
    {"ticker": "COIN", "name": "Coinbase Global, Inc.", "sector": "Financial", "industry": "Financial Data"},
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services", "industry": "Banks - Diversified"},
    {"ticker": "BAC", "name": "Bank of America Corporation", "sector": "Financial Services", "industry": "Banks - Diversified"},
    {"ticker": "GS", "name": "The Goldman Sachs Group, Inc.", "sector": "Financial Services", "industry": "Capital Markets"},
    {"ticker": "MS", "name": "Morgan Stanley", "sector": "Financial Services", "industry": "Capital Markets"},
    {"ticker": "BLK", "name": "BlackRock, Inc.", "sector": "Financial Services", "industry": "Asset Management"},
    {"ticker": "BRK-B", "name": "Berkshire Hathaway Inc.", "sector": "Financial Services", "industry": "Insurance - Diversified"},
    {"ticker": "V", "name": "Visa Inc.", "sector": "Financial Services", "industry": "Credit Services"},
    {"ticker": "MA", "name": "Mastercard Incorporated", "sector": "Financial Services", "industry": "Credit Services"},
    {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer Defensive", "industry": "Discount Stores"},
    {"ticker": "COST", "name": "Costco Wholesale Corporation", "sector": "Consumer Defensive", "industry": "Discount Stores"},
    {"ticker": "PG", "name": "The Procter & Gamble Company", "sector": "Consumer Defensive", "industry": "Household Products"},
    {"ticker": "KO", "name": "The Coca-Cola Company", "sector": "Consumer Defensive", "industry": "Beverages - Non-Alcoholic"},
    {"ticker": "PEP", "name": "PepsiCo, Inc.", "sector": "Consumer Defensive", "industry": "Beverages - Non-Alcoholic"},
    {"ticker": "DIS", "name": "The Walt Disney Company", "sector": "Communication Services", "industry": "Entertainment"},
    {"ticker": "NFLX", "name": "Netflix, Inc.", "sector": "Communication Services", "industry": "Entertainment"},
    {"ticker": "SPOT", "name": "Spotify Technology S.A.", "sector": "Communication Services", "industry": "Internet Content"},
    {"ticker": "UBER", "name": "Uber Technologies, Inc.", "sector": "Technology", "industry": "Software - Application"},
    {"ticker": "ABNB", "name": "Airbnb, Inc.", "sector": "Consumer Cyclical", "industry": "Travel Services"},
    {"ticker": "BKNG", "name": "Booking Holdings Inc.", "sector": "Consumer Cyclical", "industry": "Travel Services"},
    {"ticker": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy", "industry": "Oil & Gas Integrated"},
    {"ticker": "CVX", "name": "Chevron Corporation", "sector": "Energy", "industry": "Oil & Gas Integrated"},
    {"ticker": "LLY", "name": "Eli Lilly and Company", "sector": "Healthcare", "industry": "Drug Manufacturers - General"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Drug Manufacturers - General"},
    {"ticker": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare", "industry": "Drug Manufacturers - General"},
    {"ticker": "UNH", "name": "UnitedHealth Group Incorporated", "sector": "Healthcare", "industry": "Healthcare Plans"},
    {"ticker": "RIVN", "name": "Rivian Automotive, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    {"ticker": "LCID", "name": "Lucid Group, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"}
]

def search_securities(query: str, limit: int = 8):
    q = query.strip().upper()
    if not q:
        return POPULAR_SECURITIES[:limit]
    
    matches = []
    for s in POPULAR_SECURITIES:
        if q in s["ticker"] or q.lower() in s["name"].lower():
            matches.append(s)
            if len(matches) >= limit:
                break
    return matches
