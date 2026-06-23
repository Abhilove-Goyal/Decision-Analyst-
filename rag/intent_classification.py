# intent_classification.py

from enum import Enum

class Intent(str, Enum):
    COMMENT = "COMMENT"
    RISK = "RISK"
    EXPLAIN = "EXPLAIN"
    ANALYSE = "ANALYSE"
    GENERIC = "GENERIC"


def classify_intent(question: str) -> Intent:
    """
    Lightweight, deterministic intent classifier.
    Designed for finance / DRHP / exam-style questions.
    """
    q = question.lower().strip()

    # COMMENT
    if any(k in q for k in [
        "comment on",
        "comments on",
        "your views on",
        "brief comment",
        "give comments on"
    ]):
        return Intent.COMMENT

    # RISK
    if any(k in q for k in [
        "risk",
        "risk factors",
        "internal risks",
        "external risks",
        "what are the risks",
        "explain the risks"
    ]):
        return Intent.RISK

    # ANALYSE
    if any(k in q for k in [
        "analyse",
        "analyze",
        "evaluate",
        "critically examine",
        "assess"
    ]):
        return Intent.ANALYSE

    # EXPLAIN
    if any(k in q for k in [
        "explain",
        "describe",
        "what is",
        "how does",
        "define"
    ]):
        return Intent.EXPLAIN

    return Intent.GENERIC

STYLE_RULES = {
    "COMMENT": """
Answer as a financial or equity research analyst.
Focus on the subject itself first.
Use governance or audit references only as supporting assurance.
Write 2–3 short professional paragraphs.
""",

    "RISK": """
Answer in Draft Red Herring Prospectus (DRHP) risk-factor language.
Group risks logically.
Use cautious wording such as "may", "could", "is exposed to".
Avoid certainty or exaggeration.
""",

    "EXPLAIN": """
Explain clearly and neutrally.
Define the concept first, then elaborate.
Avoid opinions or analysis.
""",

    "ANALYSE": """
Provide balanced analysis.
Mention positives, limitations, and implications where applicable.
Maintain neutral tone.
""",

    "GENERIC": """
Answer professionally and concisely using only the context.
"""
}
