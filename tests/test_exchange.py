import unittest
from vettr.data.tickers import search_securities, CURATED_SECURITIES
from vettr.market.exchange_feed import ExchangePulseTracker

class TestExchangeAndUniverse(unittest.TestCase):
    def test_curated_securities_count(self):
        self.assertGreaterEqual(len(CURATED_SECURITIES), 80)

    def test_search_securities_curated(self):
        results = search_securities("NVDA")
        self.assertTrue(any(r["ticker"] == "NVDA" for r in results))

    def test_search_securities_sec_full_registry(self):
        # Test a ticker from the broader SEC 10,000+ index
        results = search_securities("SMCI")
        self.assertTrue(any("SMCI" in r["ticker"] for r in results))

    def test_market_status(self):
        status = ExchangePulseTracker.get_market_status()
        self.assertIsInstance(status, str)
        self.assertTrue("EXCHANGES" in status)

if __name__ == "__main__":
    unittest.main()
