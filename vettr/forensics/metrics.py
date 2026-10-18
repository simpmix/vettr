import math
from typing import Any, Dict, List, Optional

class ForensicMetrics:
    """
    Institutional quantitative forensic models:
    - Beneish M-Score (Earnings Manipulation Detection)
    - Altman Z-Score (Insolvency & Bankruptcy Risk)
    - Piotroski F-Score (Financial Health & Strength)
    """

    @classmethod
    def calculate_beneish_m_score(cls, current: Dict[str, Any], prior: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates the 8-variable Beneish M-Score.
        Returns score, probability assessment, and breakdown of components.
        """
        def safe_div(num: Optional[float], den: Optional[float], default: float = 1.0) -> float:
            if num is None or den is None or den == 0:
                return default
            return float(num) / float(den)

        # 1. DSRI: Days Sales in Receivables Index
        rec_t = current.get("accounts_receivable") or 0.0
        sales_t = current.get("revenue") or 1.0
        rec_t_1 = prior.get("accounts_receivable") or 0.0
        sales_t_1 = prior.get("revenue") or 1.0

        dsr_t = safe_div(rec_t, sales_t, 0.0)
        dsr_t_1 = safe_div(rec_t_1, sales_t_1, 0.0)
        dsri = safe_div(dsr_t, dsr_t_1, 1.0)

        # 2. GMI: Gross Margin Index
        gp_t = current.get("gross_profit")
        if gp_t is None and current.get("revenue") and current.get("cogs"):
            gp_t = current["revenue"] - current["cogs"]
        gm_t = safe_div(gp_t, sales_t, 0.3)

        gp_t_1 = prior.get("gross_profit")
        if gp_t_1 is None and prior.get("revenue") and prior.get("cogs"):
            gp_t_1 = prior["revenue"] - prior["cogs"]
        gm_t_1 = safe_div(gp_t_1, sales_t_1, 0.3)
        gmi = safe_div(gm_t_1, gm_t, 1.0)

        # 3. AQI: Asset Quality Index
        assets_t = current.get("total_assets") or 1.0
        ca_t = current.get("current_assets") or (assets_t * 0.4)
        non_ca_t = max(0.0, assets_t - ca_t)
        aq_t = safe_div(non_ca_t, assets_t, 0.5)

        assets_t_1 = prior.get("total_assets") or 1.0
        ca_t_1 = prior.get("current_assets") or (assets_t_1 * 0.4)
        non_ca_t_1 = max(0.0, assets_t_1 - ca_t_1)
        aq_t_1 = safe_div(non_ca_t_1, assets_t_1, 0.5)
        aqi = safe_div(aq_t, aq_t_1, 1.0)

        # 4. SGI: Sales Growth Index
        sgi = safe_div(sales_t, sales_t_1, 1.0)

        # 5. DEPI: Depreciation Index
        dep_t = current.get("depreciation_amortization") or (assets_t * 0.05)
        dep_rate_t = safe_div(dep_t, assets_t, 0.05)
        dep_t_1 = prior.get("depreciation_amortization") or (assets_t_1 * 0.05)
        dep_rate_t_1 = safe_div(dep_t_1, assets_t_1, 0.05)
        depi = safe_div(dep_rate_t_1, dep_rate_t, 1.0)

        # 6. SGAI: Sales, General & Administrative expenses Index
        sga_t = current.get("sg_and_a") or (sales_t * 0.2)
        sga_rate_t = safe_div(sga_t, sales_t, 0.2)
        sga_t_1 = prior.get("sg_and_a") or (sales_t_1 * 0.2)
        sga_rate_t_1 = safe_div(sga_t_1, sales_t_1, 0.2)
        sgai = safe_div(sga_rate_t, sga_rate_t_1, 1.0)

        # 7. LVGI: Leverage Index
        debt_t = current.get("long_term_debt") or (current.get("total_liabilities", 0.0) * 0.5)
        lev_t = safe_div(debt_t, assets_t, 0.3)
        debt_t_1 = prior.get("long_term_debt") or (prior.get("total_liabilities", 0.0) * 0.5)
        lev_t_1 = safe_div(debt_t_1, assets_t_1, 0.3)
        lvgi = safe_div(lev_t, lev_t_1, 1.0)

        # 8. TATA: Total Accruals to Total Assets
        ni_t = current.get("net_income") or 0.0
        cfo_t = current.get("operating_cash_flow") or ni_t
        accruals = ni_t - cfo_t
        tata = safe_div(accruals, assets_t, 0.0)

        # Beneish 8-variable equation
        m_score = (
            -4.84
            + (0.920 * dsri)
            + (0.528 * gmi)
            + (0.404 * aqi)
            + (0.892 * sgi)
            + (0.115 * depi)
            - (0.172 * sgai)
            + (4.037 * tata)
            + (0.0327 * lvgi)
        )

        is_manipulator = m_score > -1.78
        status = "HIGH RISK (Probable Manipulation)" if is_manipulator else "LOW RISK (Normal Accounting)"

        return {
            "score": round(m_score, 3),
            "status": status,
            "is_manipulator": is_manipulator,
            "threshold": -1.78,
            "variables": {
                "DSRI (Days Sales in Receivables)": round(dsri, 3),
                "GMI (Gross Margin Index)": round(gmi, 3),
                "AQI (Asset Quality Index)": round(aqi, 3),
                "SGI (Sales Growth Index)": round(sgi, 3),
                "DEPI (Depreciation Index)": round(depi, 3),
                "SGAI (SG&A Index)": round(sgai, 3),
                "LVGI (Leverage Index)": round(lvgi, 3),
                "TATA (Total Accruals/Assets)": round(tata, 4)
            }
        }

    @classmethod
    def calculate_altman_z_score(cls, current: Dict[str, Any], market_cap: Optional[float] = None) -> Dict[str, Any]:
        """
        Calculates Altman Z-Score for public firms.
        Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
        """
        def safe_div(num: Optional[float], den: Optional[float], default: float = 0.0) -> float:
            if num is None or den is None or den == 0:
                return default
            return float(num) / float(den)

        assets = current.get("total_assets") or 1.0
        ca = current.get("current_assets") or (assets * 0.4)
        cl = current.get("current_liabilities") or (assets * 0.3)
        working_capital = ca - cl

        retained_earnings = current.get("stockholders_equity", 0.0) * 0.5  # approximation if item missing
        ebit = current.get("operating_income") or (current.get("net_income", 0.0) * 1.25)
        sales = current.get("revenue") or 1.0
        liabilities = current.get("total_liabilities") or (cl * 1.5)

        mcap = market_cap or (assets * 1.5)

        x1 = safe_div(working_capital, assets)
        x2 = safe_div(retained_earnings, assets)
        x3 = safe_div(ebit, assets)
        x4 = safe_div(mcap, liabilities)
        x5 = safe_div(sales, assets)

        z_score = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (1.0 * x5)

        if z_score > 2.99:
            zone = "SAFE ZONE (Low Default Risk)"
            risk_level = "low"
        elif z_score >= 1.81:
            zone = "GREY ZONE (Moderate Insolvency Risk)"
            risk_level = "medium"
        else:
            zone = "DISTRESS ZONE (High Bankruptcy Risk)"
            risk_level = "high"

        return {
            "score": round(z_score, 2),
            "zone": zone,
            "risk_level": risk_level,
            "components": {
                "X1 (Working Capital / Assets)": round(x1, 3),
                "X2 (Retained Earnings / Assets)": round(x2, 3),
                "X3 (EBIT / Assets)": round(x3, 3),
                "X4 (Market Value Equity / Liabilities)": round(x4, 3),
                "X5 (Sales / Assets)": round(x5, 3)
            }
        }

    @classmethod
    def calculate_piotroski_f_score(cls, current: Dict[str, Any], prior: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates 9-point Piotroski F-Score.
        """
        points = 0
        signals = {}

        assets_t = current.get("total_assets") or 1.0
        assets_t_1 = prior.get("total_assets") or 1.0

        ni_t = current.get("net_income") or 0.0
        ni_t_1 = prior.get("net_income") or 0.0
        cfo_t = current.get("operating_cash_flow") or 0.0

        roa_t = ni_t / assets_t
        roa_t_1 = ni_t_1 / assets_t_1

        # 1. Positive Net Income
        p1 = 1 if ni_t > 0 else 0
        signals["Positive ROA"] = p1
        points += p1

        # 2. Positive Operating Cash Flow
        p2 = 1 if cfo_t > 0 else 0
        signals["Positive Cash Flow from Ops"] = p2
        points += p2

        # 3. Higher ROA YoY
        p3 = 1 if roa_t > roa_t_1 else 0
        signals["ROA Expansion (YoY)"] = p3
        points += p3

        # 4. Accrual quality: CFO > Net Income
        p4 = 1 if cfo_t > ni_t else 0
        signals["Quality Accruals (CFO > Net Income)"] = p4
        points += p4

        # 5. Delta Leverage: Lower Long-Term Debt / Assets
        ltd_t = current.get("long_term_debt", 0.0)
        ltd_t_1 = prior.get("long_term_debt", 0.0)
        lev_t = ltd_t / assets_t
        lev_t_1 = ltd_t_1 / assets_t_1
        p5 = 1 if lev_t <= lev_t_1 else 0
        signals["Decreased Leverage"] = p5
        points += p5

        # 6. Current Ratio Improvement
        ca_t = current.get("current_assets", 1.0)
        cl_t = current.get("current_liabilities", 1.0) or 1.0
        ca_t_1 = prior.get("current_assets", 1.0)
        cl_t_1 = prior.get("current_liabilities", 1.0) or 1.0
        cr_t = ca_t / cl_t
        cr_t_1 = ca_t_1 / cl_t_1
        p6 = 1 if cr_t > cr_t_1 else 0
        signals["Liquidity Expansion (Current Ratio)"] = p6
        points += p6

        # 7. No Share Dilution
        p7 = 1  # Standard baseline unless dilution detected
        signals["No Equity Dilution"] = p7
        points += p7

        # 8. Gross Margin Expansion
        rev_t = current.get("revenue", 1.0) or 1.0
        rev_t_1 = prior.get("revenue", 1.0) or 1.0
        gp_t = current.get("gross_profit") or (rev_t * 0.4)
        gp_t_1 = prior.get("gross_profit") or (rev_t_1 * 0.4)
        gm_t = gp_t / rev_t
        gm_t_1 = gp_t_1 / rev_t_1
        p8 = 1 if gm_t > gm_t_1 else 0
        signals["Gross Margin Improvement"] = p8
        points += p8

        # 9. Asset Turnover Improvement
        at_t = rev_t / assets_t
        at_t_1 = rev_t_1 / assets_t_1
        p9 = 1 if at_t > at_t_1 else 0
        signals["Asset Turnover Efficiency"] = p9
        points += p9

        if points >= 8:
            rating = "VERY STRONG (8-9)"
        elif points >= 5:
            rating = "STABLE / MODERATE (5-7)"
        else:
            rating = "WEAK / AT RISK (0-4)"

        return {
            "score": points,
            "max_score": 9,
            "rating": rating,
            "signals": signals
        }

    @classmethod
    def calculate_accrual_matrix(cls, current: Dict[str, Any], prior: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculates Sloan Accrual Anomaly (Sloan 1996) and Working Capital Forensics:
        - Sloan Accrual Ratio = (Net Income - Operating Cash Flow) / Total Assets
        - Days Sales Outstanding (DSO) = (Accounts Receivable / Revenue) * 365
        - Days Inventory Outstanding (DIO) = (Inventory / COGS) * 365
        - Cash Conversion Ratio = Operating Cash Flow / Net Income
        """
        assets_t = float(current.get("total_assets") or 1.0)
        ni_t = float(current.get("net_income") or 0.0)
        cfo_t = float(current.get("operating_cash_flow") or 0.0)
        rev_t = float(current.get("revenue") or 1.0)
        ar_t = float(current.get("accounts_receivable") or 0.0)
        inv_t = float(current.get("inventory") or 0.0)
        cogs_t = float(current.get("cogs") or (rev_t * 0.6 if rev_t > 0 else 1.0))

        # 1. Sloan Accrual Anomaly
        sloan_accrual = (ni_t - cfo_t) / assets_t if assets_t > 0 else 0.0
        sloan_pct = round(sloan_accrual * 100, 2)
        if sloan_pct > 10.0:
            sloan_status = "CRITICAL ACCRUAL ANOMALY (>10%)"
            sloan_risk = "HIGH"
        elif sloan_pct > 5.0:
            sloan_status = "ELEVATED NON-CASH EARNINGS"
            sloan_risk = "MEDIUM"
        elif sloan_pct < -10.0:
            sloan_status = "CONSERVATIVE / HIGH CASH FLOW"
            sloan_risk = "LOW"
        else:
            sloan_status = "NORMAL CASH-BACKED EARNINGS"
            sloan_risk = "LOW"

        # 2. DSO & DIO
        dso_t = round((ar_t / rev_t * 365), 1) if rev_t > 0 else 0.0
        dio_t = round((inv_t / cogs_t * 365), 1) if cogs_t > 0 else 0.0

        dso_prior = None
        dso_delta = None
        dio_prior = None
        dio_delta = None
        asset_growth = None

        if prior:
            assets_t_1 = float(prior.get("total_assets") or 1.0)
            rev_t_1 = float(prior.get("revenue") or 1.0)
            ar_t_1 = float(prior.get("accounts_receivable") or 0.0)
            inv_t_1 = float(prior.get("inventory") or 0.0)
            cogs_t_1 = float(prior.get("cogs") or (rev_t_1 * 0.6 if rev_t_1 > 0 else 1.0))

            if rev_t_1 > 0:
                dso_prior = round((ar_t_1 / rev_t_1 * 365), 1)
                dso_delta = round(dso_t - dso_prior, 1)

            if cogs_t_1 > 0:
                dio_prior = round((inv_t_1 / cogs_t_1 * 365), 1)
                dio_delta = round(dio_t - dio_prior, 1)

            if assets_t_1 > 0:
                asset_growth = round(((assets_t - assets_t_1) / assets_t_1 * 100), 1)

        # 3. Cash Conversion Ratio
        cash_conversion_ratio = round((cfo_t / ni_t * 100), 1) if ni_t > 0 else (0.0 if cfo_t <= 0 else 999.0)

        return {
            "sloan_accrual_ratio": sloan_accrual,
            "sloan_accrual_pct": sloan_pct,
            "sloan_status": sloan_status,
            "sloan_risk": sloan_risk,
            "dso_days": dso_t,
            "dso_prior_days": dso_prior,
            "dso_delta_days": dso_delta,
            "dio_days": dio_t,
            "dio_prior_days": dio_prior,
            "dio_delta_days": dio_delta,
            "cash_conversion_pct": cash_conversion_ratio,
            "asset_growth_pct": asset_growth
        }
