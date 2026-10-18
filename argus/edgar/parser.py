import re
import warnings
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

class EdgarParser:
    """
    Parses SEC 10-K, 10-Q filings:
    - Extracts Item 1A (Risk Factors), Item 7 (MD&A), Controls
    - Extracts standardized GAAP financial time-series from XBRL Company Facts
    """

    # Common GAAP concept variations used by companies
    CONCEPT_MAP = {
        "revenue": [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet",
            "SalesRevenueGoodsNet"
        ],
        "net_income": [
            "NetIncomeLoss",
            "ProfitLoss"
        ],
        "operating_income": [
            "OperatingIncomeLoss"
        ],
        "total_assets": [
            "Assets"
        ],
        "current_assets": [
            "AssetsCurrent"
        ],
        "total_liabilities": [
            "Liabilities"
        ],
        "current_liabilities": [
            "LiabilitiesCurrent"
        ],
        "stockholders_equity": [
            "StockholdersEquity",
            "CommonStockholdersEquity"
        ],
        "operating_cash_flow": [
            "NetCashProvidedByUsedInOperatingActivities"
        ],
        "accounts_receivable": [
            "AccountsReceivableNetCurrent",
            "ReceivablesNetCurrent"
        ],
        "inventory": [
            "InventoryNet"
        ],
        "gross_profit": [
            "GrossProfit"
        ],
        "cogs": [
            "CostOfGoodsAndServicesSold",
            "CostOfGoodsSold"
        ],
        "sg_and_a": [
            "SellingGeneralAndAdministrativeExpense",
            "GeneralAndAdministrativeExpense"
        ],
        "long_term_debt": [
            "LongTermDebtNoncurrent",
            "LongTermDebt"
        ],
        "depreciation_amortization": [
            "DepreciationDepletionAndAmortization",
            "DepreciationAndAmortization"
        ]
    }

    @classmethod
    def extract_xbrl_annual_series(cls, facts_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts annual (10-K, fp='FY') financial records sorted by fiscal year.
        Returns a list of dicts: [{fiscal_year, end_date, revenue, net_income, ...}]
        """
        gaap = facts_data.get("facts", {}).get("us-gaap", {})
        if not gaap:
            return []

        years_data: Dict[int, Dict[str, Any]] = {}

        for canonical_name, concepts in cls.CONCEPT_MAP.items():
            for c in concepts:
                if c in gaap and "units" in gaap[c]:
                    concept_obj = gaap[c]
                    units = concept_obj.get("units", {})
                    entries = units.get("USD", [])
                    for entry in entries:
                        form = entry.get("form")
                        fp = entry.get("fp")
                        fy = entry.get("fy")
                        val = entry.get("val")

                        # Filter for annual 10-K entries
                        if form in ("10-K", "10-K/A") and fp == "FY" and fy:
                            if fy not in years_data:
                                years_data[fy] = {
                                    "fiscal_year": fy,
                                    "end_date": entry.get("end", "")
                                }
                            # Populate canonical field if not yet set
                            if canonical_name not in years_data[fy] or years_data[fy][canonical_name] == 0:
                                years_data[fy][canonical_name] = val

        sorted_years = sorted(years_data.values(), key=lambda x: x["fiscal_year"])
        return sorted_years

    @classmethod
    def extract_item_sections(cls, html_content: str) -> Dict[str, str]:
        """
        Extracts core disclosure items from 10-K / 10-Q HTML:
        - Item 1A: Risk Factors
        - Item 7: Management's Discussion and Analysis (MD&A)
        - Item 9A: Controls and Procedures
        """
        soup = BeautifulSoup(html_content, "lxml")
        
        # Remove scripts, styles, metadata
        for s in soup(["script", "style", "meta", "noscript"]):
            s.decompose()

        text = soup.get_text("\n")
        # Normalize excessive whitespace
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        full_clean_text = "\n".join(lines)

        sections = {
            "item_1a_risk_factors": cls._extract_section_text(
                full_clean_text,
                start_pattern=r"(ITEM\s+1A[\.\:\s\-]+RISK\s+FACTORS)",
                end_pattern=r"(ITEM\s+(?:1B|2|7)[\.\:\s\-])"
            ),
            "item_7_mda": cls._extract_section_text(
                full_clean_text,
                start_pattern=r"(ITEM\s+7[\.\:\s\-]+MANAGEMENT[\'’]S\s+DISCUSSION)",
                end_pattern=r"(ITEM\s+(?:7A|8)[\.\:\s\-])"
            ),
            "item_9a_controls": cls._extract_section_text(
                full_clean_text,
                start_pattern=r"(ITEM\s+9A[\.\:\s\-]+CONTROLS\s+AND\s+PROCEDURES)",
                end_pattern=r"(ITEM\s+(?:9B|10)[\.\:\s\-])"
            )
        }

        return sections

    @staticmethod
    def _extract_section_text(text: str, start_pattern: str, end_pattern: str, max_chars: int = 50000) -> str:
        matches = list(re.finditer(start_pattern, text, re.IGNORECASE))
        if not matches:
            return ""

        # Usually the first match in a 10-K is in the Table of Contents,
        # and the second match is the actual detailed section body.
        start_idx = matches[-1].start() if len(matches) > 1 else matches[0].start()

        subtext = text[start_idx:]
        end_match = re.search(end_pattern, subtext[200:], re.IGNORECASE)
        if end_match:
            section_content = subtext[: 200 + end_match.start()]
        else:
            section_content = subtext[:max_chars]

        return section_content.strip()
