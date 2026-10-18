import difflib
import re
from typing import Any, Dict, List

class FilingDiffer:
    """
    Computes structural and sentence-level diffs between consecutive SEC filings (e.g. 10-K vs prior 10-K).
    Detects silently inserted risk factors, deleted disclaimers, and modified language.
    """

    @classmethod
    def split_into_sentences(cls, text: str) -> List[str]:
        # Clean text
        cleaned = re.sub(r"\s+", " ", text).strip()
        # Split on sentence boundaries
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", cleaned)
        return [s.strip() for s in sentences if len(s.strip()) > 25]

    @classmethod
    def compare_sections(cls, current_text: str, prior_text: str, max_samples: int = 15) -> Dict[str, Any]:
        """
        Calculates diff statistics and extracts most significant added/removed disclosure blocks.
        """
        curr_sentences = cls.split_into_sentences(current_text)
        prior_sentences = cls.split_into_sentences(prior_text)

        if not curr_sentences and not prior_sentences:
            return {
                "similarity_ratio": 1.0,
                "added_disclosures": [],
                "removed_disclosures": [],
                "summary": "No textual content available to compare."
            }

        matcher = difflib.SequenceMatcher(None, prior_sentences, curr_sentences)
        similarity = matcher.ratio()

        added = []
        removed = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "insert":
                for idx in range(j1, j2):
                    added.append(curr_sentences[idx])
            elif tag == "delete":
                for idx in range(i1, i2):
                    removed.append(prior_sentences[idx])
            elif tag == "replace":
                for idx in range(j1, j2):
                    added.append(curr_sentences[idx])
                for idx in range(i1, i2):
                    removed.append(prior_sentences[idx])

        # Filter out boilerplate sentences
        def is_substantive(s: str) -> bool:
            lower = s.lower()
            return not (
                "table of contents" in lower
                or "item 1a." in lower
                or "item 7." in lower
                or len(s) < 40
            )

        substantive_added = [s for s in added if is_substantive(s)]
        substantive_removed = [s for s in removed if is_substantive(s)]

        return {
            "similarity_ratio": round(similarity, 3),
            "similarity_pct": round(similarity * 100, 1),
            "added_count": len(substantive_added),
            "removed_count": len(substantive_removed),
            "sample_added": substantive_added[:max_samples],
            "sample_removed": substantive_removed[:max_samples],
            "total_current_sentences": len(curr_sentences),
            "total_prior_sentences": len(prior_sentences)
        }
