import logging
from typing import Any, Dict, List, Optional
from vettr.edgar.client import EdgarClient
from vettr.edgar.parser import EdgarParser
from vettr.edgar.insiders import InsiderScanner
from vettr.forensics.metrics import ForensicMetrics
from vettr.forensics.anomalies import AnomalyDetector
from vettr.forensics.sentiment import FinancialSentiment
from vettr.forensics.dupont import DuPontAnalyzer
from vettr.diff.differ import FilingDiffer
from vettr.market.provider import MarketDataProvider
from vettr.export.dossier import DossierGenerator

logger = logging.getLogger(__name__)

class VettrEngine:
    """
    Autonomous Financial Forensics & Regulatory Intelligence Pipeline.
    Orchestrates SEC EDGAR data, quantitative models, filing diffs, Form 4 insider trades, and market quotes.
    """

    def __init__(self):
        self.edgar = EdgarClient()
        self.insiders = InsiderScanner(self.edgar)

    def analyze_ticker(self, ticker: str) -> Dict[str, Any]:
        """Runs the complete end-to-end forensic analysis for a ticker."""
        clean_ticker = ticker.strip().upper()
        logger.info(f"Starting VETTR Forensic Analysis for {clean_ticker}")

        # 1. Market Data Overview
        market_data = MarketDataProvider.get_market_overview(clean_ticker)

        # 2. CIK Resolution
        cik = self.edgar.get_cik_for_ticker(clean_ticker)
        if not cik:
            return {
                "ticker": clean_ticker,
                "error": f"Ticker '{clean_ticker}' not found in SEC EDGAR registry.",
                "market_data": market_data
            }

        # 3. SEC Filings List
        recent_10k_filings = self.edgar.get_filing_list(cik, form_types=["10-K", "10-K/A"], limit=5)
        recent_8k_filings = self.edgar.get_filing_list(cik, form_types=["8-K"], limit=10)
        recent_all_filings = self.edgar.get_filing_list(cik, limit=20)

        # 4. Standardized XBRL Financials
        annual_series = []
        try:
            facts = self.edgar.get_company_facts(cik)
            annual_series = EdgarParser.extract_xbrl_annual_series(facts)
        except Exception as e:
            logger.warning(f"Could not load SEC XBRL facts for {clean_ticker}: {e}")

        # 5. Quantitative Forensic Scores & DuPont Analysis
        beneish = None
        altman = None
        piotroski = None
        accrual_matrix = None
        financial_anomalies = []
        dupont_series = []

        if len(annual_series) >= 2:
            current_fy = annual_series[-1]
            prior_fy = annual_series[-2]

            market_cap = market_data.get("market_cap")
            beneish = ForensicMetrics.calculate_beneish_m_score(current_fy, prior_fy)
            altman = ForensicMetrics.calculate_altman_z_score(current_fy, market_cap=market_cap)
            piotroski = ForensicMetrics.calculate_piotroski_f_score(current_fy, prior_fy)
            accrual_matrix = ForensicMetrics.calculate_accrual_matrix(current_fy, prior_fy)
            financial_anomalies = AnomalyDetector.analyze_financial_anomalies(current_fy, prior_fy)
            dupont_series = [DuPontAnalyzer.decompose_roe(rec) for rec in annual_series[-5:]]
        elif len(annual_series) == 1:
            current_fy = annual_series[-1]
            altman = ForensicMetrics.calculate_altman_z_score(current_fy, market_cap=market_data.get("market_cap"))
            accrual_matrix = ForensicMetrics.calculate_accrual_matrix(current_fy)
            dupont_series = [DuPontAnalyzer.decompose_roe(current_fy)]

        # 6. Qualitative Disclosure Analysis & Text Diff
        sections_latest = {}
        sections_prior = {}
        regulatory_flags = []
        sentiment_analysis = None
        diff_analysis = None

        if recent_10k_filings:
            try:
                # Latest 10-K
                latest_url = recent_10k_filings[0]["url"]
                latest_html = self.edgar.fetch_filing_content(latest_url)
                sections_latest = EdgarParser.extract_item_sections(latest_html)

                regulatory_flags = AnomalyDetector.scan_regulatory_text_flags(sections_latest)
                
                # Sentiment on Risk Factors / MD&A
                risk_text = sections_latest.get("item_1a_risk_factors", "")
                mda_text = sections_latest.get("item_7_mda", "")
                sentiment_target = risk_text if len(risk_text) > 500 else mda_text
                if sentiment_target:
                    sentiment_analysis = FinancialSentiment.analyze_tone(sentiment_target)

                # Prior 10-K Diff
                if len(recent_10k_filings) >= 2:
                    prior_url = recent_10k_filings[1]["url"]
                    prior_html = self.edgar.fetch_filing_content(prior_url)
                    sections_prior = EdgarParser.extract_item_sections(prior_html)

                    diff_analysis = FilingDiffer.compare_sections(
                        current_text=sections_latest.get("item_1a_risk_factors", ""),
                        prior_text=sections_prior.get("item_1a_risk_factors", "")
                    )
            except Exception as e:
                logger.error(f"Error parsing filing disclosures for {clean_ticker}: {e}")

        # 7. Form 4 Insider Trading Activity
        insider_data = {"trades": [], "sentiment": "NEUTRAL"}
        try:
            insider_data = self.insiders.get_recent_insider_trades(cik, limit=12)
        except Exception as e:
            logger.warning(f"Could not load Form 4 insider activity for {clean_ticker}: {e}")

        # 8. Reverse DCF & Implied Growth Calculation
        valuation_model = self._calculate_implied_growth(market_data, annual_series)

        # 9. Aggregate Risk Score (Composite 0 - 100)
        risk_score = 15  # Baseline
        if beneish and beneish.get("is_manipulator"):
            risk_score += 35
        if altman:
            if altman.get("risk_level") == "high":
                risk_score += 30
            elif altman.get("risk_level") == "medium":
                risk_score += 15
        if piotroski and piotroski.get("score", 9) <= 4:
            risk_score += 15
        if accrual_matrix and accrual_matrix.get("sloan_risk") == "HIGH":
            risk_score += 20
        elif accrual_matrix and accrual_matrix.get("sloan_risk") == "MEDIUM":
            risk_score += 10
        if len(financial_anomalies) > 0:
            risk_score += min(len(financial_anomalies) * 10, 25)
        if len(regulatory_flags) > 0:
            risk_score += min(len(regulatory_flags) * 8, 20)
        if insider_data.get("sentiment") == "HEAVY INSIDER SELLING":
            risk_score += 10

        risk_score = min(100, max(0, risk_score))

        # Performance & Growth Metrics
        growth_metrics = {}
        if len(annual_series) >= 2:
            latest = annual_series[-1]
            rev_t = float(latest.get("revenue") or 0.0)
            ni_t = float(latest.get("net_income") or 0.0)
            cfo_t = float(latest.get("operating_cash_flow") or 0.0)

            cagr_rev = None
            cagr_ni = None
            if len(annual_series) >= 4:
                base = annual_series[-4]
                rev_0 = float(base.get("revenue") or 0.0)
                ni_0 = float(base.get("net_income") or 0.0)
                if rev_0 > 0 and rev_t > 0:
                    cagr_rev = round(((rev_t / rev_0) ** (1/3) - 1) * 100, 1)
                if ni_0 > 0 and ni_t > 0:
                    cagr_ni = round(((ni_t / ni_0) ** (1/3) - 1) * 100, 1)

            cash_conversion = round((cfo_t / ni_t * 100), 1) if ni_t > 0 else None

            ebit = float(latest.get("operating_income") or (ni_t * 1.25))
            nopat = ebit * 0.79
            assets = float(latest.get("total_assets") or 1.0)
            cl = float(latest.get("current_liabilities") or (assets * 0.3))
            invested_capital = max(1.0, assets - cl)
            roic = round((nopat / invested_capital * 100), 1)

            growth_metrics = {
                "cagr_revenue_3yr": cagr_rev,
                "cagr_net_income_3yr": cagr_ni,
                "cash_conversion_pct": cash_conversion,
                "roic_pct": roic,
                "sloan_accrual_pct": accrual_matrix.get("sloan_accrual_pct") if accrual_matrix else None,
                "sloan_status": accrual_matrix.get("sloan_status") if accrual_matrix else "NORMAL",
                "dso_days": accrual_matrix.get("dso_days") if accrual_matrix else None,
                "dio_days": accrual_matrix.get("dio_days") if accrual_matrix else None
            }

        # Executive Forensic Synthesis Narrative
        synthesis_parts = []
        if beneish:
            if beneish.get("is_manipulator"):
                synthesis_parts.append(f"Beneish M-Score ({beneish.get('score')}) triggers earnings manipulation threshold (-1.78)")
            else:
                synthesis_parts.append(f"Beneish M-Score ({beneish.get('score')}) indicates low probability of accounting manipulation")

        if altman:
            synthesis_parts.append(f"Altman Z-Score ({altman.get('score')}) places entity in {altman.get('zone')}")

        if piotroski:
            synthesis_parts.append(f"Piotroski F-Score ({piotroski.get('score')}/9) reflects {piotroski.get('rating')}")

        if accrual_matrix:
            s_pct = accrual_matrix.get("sloan_accrual_pct", 0)
            if s_pct > 10.0:
                synthesis_parts.append(f"Sloan Accrual Anomaly flagged (+{s_pct}%), indicating earnings non-cash decoupling")
            else:
                synthesis_parts.append(f"Accruals are cash-backed (Sloan Ratio: {s_pct:+.1f}%)")

        if financial_anomalies:
            synthesis_parts.append(f"{len(financial_anomalies)} financial statement divergence surfaced")

        executive_synthesis = ". ".join(synthesis_parts) + "."

        return {
            "ticker": clean_ticker,
            "cik": cik,
            "market_data": market_data,
            "risk_score": risk_score,
            "executive_synthesis": executive_synthesis,
            "forensics": {
                "beneish_m_score": beneish,
                "altman_z_score": altman,
                "piotroski_f_score": piotroski,
                "accrual_matrix": accrual_matrix,
                "anomalies": financial_anomalies,
                "regulatory_flags": regulatory_flags,
                "sentiment": sentiment_analysis
            },
            "growth_metrics": growth_metrics,
            "financial_series": annual_series[-5:],  # Last 5 fiscal years
            "dupont_series": dupont_series,
            "valuation_model": valuation_model,
            "diff_analysis": diff_analysis,
            "insider_activity": insider_data,
            "filings": {
                "recent_10k": recent_10k_filings,
                "recent_8k": recent_8k_filings,
                "all_recent": recent_all_filings[:15]
            }
        }

    def _calculate_implied_growth(self, market_data: Dict[str, Any], annual_series: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates Reverse DCF growth rate implied by current market valuation."""
        mcap = market_data.get("market_cap") or 0.0
        pe = market_data.get("trailing_pe")
        
        cfo = 0.0
        ni = 0.0
        if annual_series:
            cfo = float(annual_series[-1].get("operating_cash_flow") or 0.0)
            ni = float(annual_series[-1].get("net_income") or 0.0)

        fcf_est = cfo * 0.85 if cfo > 0 else (ni if ni > 0 else 0.0)
        
        # Reverse DCF implied 10-year FCF growth rate at 10% discount rate and 3% terminal growth
        implied_growth = 0.0
        if mcap > 0 and fcf_est > 0:
            fcf_yield = (fcf_est / mcap) * 100
            # Rough approximation: Implied growth = Discount Rate (10%) - FCF Yield
            implied_growth = max(0.0, 10.0 - fcf_yield + 4.0)

        return {
            "fcf_estimate": round(fcf_est, 2),
            "fcf_yield_pct": round((fcf_est / mcap * 100), 2) if mcap > 0 else 0.0,
            "implied_growth_10yr_pct": round(implied_growth, 1),
            "discount_rate_pct": 10.0,
            "terminal_growth_pct": 3.0,
            "valuation_verdict": "AGGRESSIVE GROWTH PRICED IN" if implied_growth > 20 else ("MODERATE GROWTH EXPECTATIONS" if implied_growth > 8 else "LOW GROWTH / VALUE PRICING")
        }

    def generate_dossier_markdown(self, ticker: str) -> str:
        report = self.analyze_ticker(ticker)
        return DossierGenerator.generate_markdown_dossier(report)

# Backward-compatible alias
ArgusEngine = VettrEngine
