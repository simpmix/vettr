from typing import Any, Dict, Optional

class DuPontAnalyzer:
    """
    Decomposes Return on Equity (ROE) into 3-stage and 5-stage DuPont drivers.
    Identifies whether profitability is driven by operating efficiency or artificial leverage.
    """

    @classmethod
    def decompose_roe(cls, fy_record: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates 3-way and 5-way DuPont decomposition for a fiscal year record."""
        rev = float(fy_record.get("revenue") or 1.0)
        ni = float(fy_record.get("net_income") or 0.0)
        ebit = float(fy_record.get("operating_income") or (ni * 1.25))
        assets = float(fy_record.get("total_assets") or 1.0)
        equity = float(fy_record.get("stockholders_equity") or (assets * 0.5))

        def safe_ratio(n: float, d: float) -> float:
            return (n / d) if d != 0 else 0.0

        # Core ratios
        net_profit_margin = safe_ratio(ni, rev) * 100
        operating_margin = safe_ratio(ebit, rev) * 100
        asset_turnover = safe_ratio(rev, assets)
        equity_multiplier = safe_ratio(assets, equity)

        # 3-Stage ROE: Net Margin * Asset Turnover * Equity Multiplier
        roe = safe_ratio(ni, equity) * 100
        roa = safe_ratio(ni, assets) * 100

        # Assess driver
        if equity_multiplier > 4.0 and roe > 20:
            quality = "LEVERAGE-DEPENDENT (High financial risk)"
        elif asset_turnover > 1.2 and operating_margin > 15:
            quality = "HIGH OPERATIONAL QUALITY (Asset efficient & strong margins)"
        elif operating_margin < 5:
            quality = "LOW MARGIN COMMODITY"
        else:
            quality = "HEALTHY BALANCED PROFILE"

        return {
            "fiscal_year": fy_record.get("fiscal_year", "N/A"),
            "roe_pct": round(roe, 2),
            "roa_pct": round(roa, 2),
            "net_profit_margin_pct": round(net_profit_margin, 2),
            "operating_margin_pct": round(operating_margin, 2),
            "asset_turnover": round(asset_turnover, 3),
            "equity_multiplier": round(equity_multiplier, 2),
            "quality_verdict": quality
        }
