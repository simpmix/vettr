import re
from typing import Any, Dict, List, Optional

class AnomalyDetector:
    """
    Forensic Accounting Anomaly & Red Flag Detector.
    Identifies aggressive revenue recognition, cash-flow divergences,
    balance sheet bloat, and regulatory disclosure red flags.
    """

    CRITICAL_LEGAL_KEYWORDS = [
        "material weakness",
        "restatement",
        "internal control deficiency",
        "subpoena",
        "formal investigation",
        "formal inquiry",
        "accounting error",
        "wells notice",
        "resignation of auditor",
        "disagreement with former accountants",
        "going concern",
        "whistleblower"
    ]

    @classmethod
    def analyze_financial_anomalies(cls, current: Dict[str, Any], prior: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scans quantitative balance sheet & income statement divergences."""
        flags = []

        rev_t = current.get("revenue") or 0.0
        rev_t_1 = prior.get("revenue") or 0.0
        rev_growth = ((rev_t - rev_t_1) / rev_t_1 * 100) if rev_t_1 > 0 else 0.0

        ni_t = current.get("net_income") or 0.0
        ni_t_1 = prior.get("net_income") or 0.0
        cfo_t = current.get("operating_cash_flow") or 0.0

        ar_t = current.get("accounts_receivable") or 0.0
        ar_t_1 = prior.get("accounts_receivable") or 0.0
        ar_growth = ((ar_t - ar_t_1) / ar_t_1 * 100) if ar_t_1 > 0 else 0.0

        inv_t = current.get("inventory") or 0.0
        inv_t_1 = prior.get("inventory") or 0.0
        inv_growth = ((inv_t - inv_t_1) / inv_t_1 * 100) if inv_t_1 > 0 else 0.0

        # Flag 1: Net Income vs Operating Cash Flow Divergence
        if ni_t > 0 and cfo_t < (ni_t * 0.5):
            severity = "HIGH" if cfo_t <= 0 else "MEDIUM"
            flags.append({
                "type": "CASH_FLOW_DIVERGENCE",
                "severity": severity,
                "title": "Severe Operating Cash Flow vs Net Income Divergence",
                "description": (
                    f"Reported Net Income of ${ni_t:,.0f} is not matched by cash generation "
                    f"(Operating Cash Flow was only ${cfo_t:,.0f}). This indicates high non-cash "
                    f"accruals and potential aggressive earnings recognition."
                ),
                "metric": f"CFO/NI Ratio: {(cfo_t / ni_t):.2f}" if ni_t != 0 else "N/A"
            })

        # Flag 2: Channel Stuffing / Receivables Decoupling
        if ar_growth > (rev_growth + 20.0) and ar_growth > 15.0:
            flags.append({
                "type": "RECEIVABLES_SURGE",
                "severity": "HIGH",
                "title": "Accounts Receivable Surging Faster Than Revenue",
                "description": (
                    f"Accounts Receivable grew {ar_growth:.1f}% YoY, while Revenue only grew "
                    f"{rev_growth:.1f}%. Classic indicator of channel stuffing, uncollected sales, "
                    f"or loosening credit terms to fabricate growth."
                ),
                "metric": f"DSO Growth Gap: +{ar_growth - rev_growth:.1f}%"
            })

        # Flag 3: Inventory Stacking / Demand Freeze
        if inv_growth > (rev_growth + 25.0) and inv_t > 0:
            flags.append({
                "type": "INVENTORY_BLOAT",
                "severity": "MEDIUM",
                "title": "Inventory Bloat Disconnected from Sales",
                "description": (
                    f"Inventories expanded by {inv_growth:.1f}%, outpacing Revenue growth "
                    f"({rev_growth:.1f}%). Risks impending inventory write-downs and gross margin erosion."
                ),
                "metric": f"Inventory Gap: +{inv_growth - rev_growth:.1f}%"
            })

        # Flag 4: Gross Margin Deterioration
        gp_t = current.get("gross_profit")
        gp_t_1 = prior.get("gross_profit")
        if gp_t and gp_t_1 and rev_t > 0 and rev_t_1 > 0:
            gm_t = (gp_t / rev_t) * 100
            gm_t_1 = (gp_t_1 / rev_t_1) * 100
            if (gm_t_1 - gm_t) > 5.0:
                flags.append({
                    "type": "MARGIN_COMPRESSION",
                    "severity": "MEDIUM",
                    "title": "Rapid Gross Margin Compression",
                    "description": (
                        f"Gross margin dropped from {gm_t_1:.1f}% to {gm_t:.1f}% "
                        f"(-{gm_t_1 - gm_t:.1f}% bps). Points to lost pricing power or cost inflation."
                    ),
                    "metric": f"Delta GM: -{gm_t_1 - gm_t:.1f}%"
                })

        return flags

    @classmethod
    def scan_regulatory_text_flags(cls, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scans extracted SEC sections for high-risk legal and audit triggers."""
        text_flags = []
        combined_text = " ".join(sections.values()).lower()

        for kw in cls.CRITICAL_LEGAL_KEYWORDS:
            matches = list(re.finditer(r"\b" + re.escape(kw) + r"\b", combined_text))
            if matches:
                # Extract surrounding excerpt context
                first_idx = matches[0].start()
                start_context = max(0, first_idx - 150)
                end_context = min(len(combined_text), first_idx + 250)
                excerpt = combined_text[start_context:end_context].replace("\n", " ").strip()

                text_flags.append({
                    "keyword": kw,
                    "count": len(matches),
                    "severity": "CRITICAL" if kw in ("material weakness", "restatement", "wells notice", "subpoena") else "HIGH",
                    "title": f"Filing Discloses: '{kw.title()}' ({len(matches)} mentions)",
                    "excerpt": f"...{excerpt}..."
                })

        return text_flags
