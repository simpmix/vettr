import re
from typing import Any, Dict

class FinancialSentiment:
    """
    Loughran-McDonald (LM) Domain-Specific Financial Sentiment Analyzer.
    Optimized specifically for 10-K, 10-Q, and MD&A disclosure texts.
    """

    LM_NEGATIVE = {
        "loss", "losses", "adverse", "adversely", "impairment", "impaired",
        "default", "defaults", "termination", "penalties", "penalty", "breach",
        "failure", "fail", "restatement", "restated", "deficit", "decline",
        "declined", "deterioration", "slowdown", "weakness", "weaknesses",
        "drop", "dropped", "downturn", "disruption", "disruptions", "write-down",
        "shortfall", "insolvency", "delinquent", "delinquency"
    }

    LM_UNCERTAINTY = {
        "approximate", "approximately", "uncertain", "uncertainty", "uncertainties",
        "contingency", "contingencies", "fluctuate", "fluctuating", "fluctuation",
        "pending", "unpredictable", "doubtful", "unresolved", "assumption",
        "assumptions", "risk", "risks", "speculative", "volatility", "volatile",
        "variability", "estimate", "estimated", "estimates", "exposure", "exposures"
    }

    LM_LITIGIOUS = {
        "litigation", "lawsuit", "lawsuits", "action", "actions", "claim", "claims",
        "claimant", "dispute", "disputes", "settlement", "settlements", "arbitration",
        "counterclaim", "jurisdiction", "subpoena", "subpoenas", "investigation",
        "investigations", "proceeding", "proceedings", "plaintiff", "defendant",
        "injunction", "infringement", "indemnify", "indemnification", "indemnity"
    }

    LM_CONSTRAINING = {
        "bound", "covenant", "covenants", "restriction", "restrictions", "restrictive",
        "obligations", "obligation", "committed", "commitment", "commitments",
        "condition", "conditions", "mandate", "mandated", "prohibit", "prohibited",
        "required", "requirement", "requirements", "stipulation"
    }

    LM_POSITIVE = {
        "advantage", "advantages", "profitable", "profitability", "exceed", "exceeded",
        "gain", "gains", "growth", "growing", "innovative", "innovation", "outperform",
        "outperformed", "strength", "strengths", "successful", "successfully",
        "upside", "expansion", "momentum", "robust", "efficient", "efficiency"
    }

    @classmethod
    def analyze_tone(cls, text: str) -> Dict[str, Any]:
        """Analyzes text against the Loughran-McDonald categories."""
        tokens = re.findall(r"\b[a-zA-Z\-]+\b", text.lower())
        total_words = len(tokens)
        if total_words == 0:
            return {
                "total_words": 0,
                "negative_score": 0.0,
                "uncertainty_score": 0.0,
                "litigious_score": 0.0,
                "constraining_score": 0.0,
                "positive_score": 0.0,
                "tone_ratio": "Neutral"
            }

        neg_count = sum(1 for w in tokens if w in cls.LM_NEGATIVE)
        unc_count = sum(1 for w in tokens if w in cls.LM_UNCERTAINTY)
        lit_count = sum(1 for w in tokens if w in cls.LM_LITIGIOUS)
        con_count = sum(1 for w in tokens if w in cls.LM_CONSTRAINING)
        pos_count = sum(1 for w in tokens if w in cls.LM_POSITIVE)

        neg_pct = (neg_count / total_words) * 100
        unc_pct = (unc_count / total_words) * 100
        lit_pct = (lit_count / total_words) * 100
        con_pct = (con_count / total_words) * 100
        pos_pct = (pos_count / total_words) * 100

        # Tone rating
        if neg_pct > (pos_pct * 1.5) or unc_pct > 2.5:
            tone = "CAUTIONARY / DEFENSIVE"
        elif pos_pct > (neg_pct * 1.5):
            tone = "OPTIMISTIC / EXPANSIONARY"
        else:
            tone = "BALANCED / PRUDENT"

        return {
            "total_words": total_words,
            "tone": tone,
            "negative_pct": round(neg_pct, 2),
            "uncertainty_pct": round(unc_pct, 2),
            "litigious_pct": round(lit_pct, 2),
            "constraining_pct": round(con_pct, 2),
            "positive_pct": round(pos_pct, 2),
            "counts": {
                "negative": neg_count,
                "uncertainty": unc_count,
                "litigious": lit_count,
                "constraining": con_count,
                "positive": pos_count
            }
        }
