import unittest
from vettr.forensics.metrics import ForensicMetrics
from vettr.forensics.anomalies import AnomalyDetector
from vettr.forensics.dupont import DuPontAnalyzer

class TestForensicSuite(unittest.TestCase):
    def setUp(self):
        self.clean_prior = {
            "fiscal_year": 2023,
            "revenue": 100_000_000.0,
            "net_income": 12_000_000.0,
            "operating_income": 15_000_000.0,
            "total_assets": 120_000_000.0,
            "current_assets": 50_000_000.0,
            "total_liabilities": 40_000_000.0,
            "current_liabilities": 25_000_000.0,
            "stockholders_equity": 80_000_000.0,
            "operating_cash_flow": 14_000_000.0,
            "accounts_receivable": 15_000_000.0,
            "inventory": 10_000_000.0,
            "gross_profit": 40_000_000.0,
            "cogs": 60_000_000.0
        }

        self.clean_current = {
            "fiscal_year": 2024,
            "revenue": 115_000_000.0,
            "net_income": 15_000_000.0,
            "operating_income": 18_000_000.0,
            "total_assets": 135_000_000.0,
            "current_assets": 60_000_000.0,
            "total_liabilities": 45_000_000.0,
            "current_liabilities": 28_000_000.0,
            "stockholders_equity": 90_000_000.0,
            "operating_cash_flow": 17_000_000.0,
            "accounts_receivable": 17_000_000.0,
            "inventory": 11_000_000.0,
            "gross_profit": 46_000_000.0,
            "cogs": 69_000_000.0
        }

    def test_altman_z_score_safe(self):
        z = ForensicMetrics.calculate_altman_z_score(self.clean_current, market_cap=200_000_000.0)
        self.assertGreater(z["score"], 2.99)
        self.assertEqual(z["risk_level"], "low")

    def test_beneish_m_score_clean(self):
        m = ForensicMetrics.calculate_beneish_m_score(self.clean_current, self.clean_prior)
        self.assertLess(m["score"], -1.78)
        self.assertFalse(m["is_manipulator"])

    def test_piotroski_f_score_high(self):
        f = ForensicMetrics.calculate_piotroski_f_score(self.clean_current, self.clean_prior)
        self.assertGreaterEqual(f["score"], 7)

    def test_cash_flow_divergence_flag(self):
        bad_current = dict(self.clean_current)
        bad_current["operating_cash_flow"] = 2_000_000.0
        anomalies = AnomalyDetector.analyze_financial_anomalies(bad_current, self.clean_prior)
        flag_types = [a["type"] for a in anomalies]
        self.assertIn("CASH_FLOW_DIVERGENCE", flag_types)

    def test_dupont_decomposition(self):
        d = DuPontAnalyzer.decompose_roe(self.clean_current)
        self.assertGreater(d["roe_pct"], 0)
        self.assertGreater(d["asset_turnover"], 0)
        self.assertGreater(d["equity_multiplier"], 1.0)

if __name__ == "__main__":
    unittest.main()
