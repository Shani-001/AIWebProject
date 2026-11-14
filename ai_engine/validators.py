import re
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from config.settings import VALID_CATEGORIES


class SignalItem(BaseModel):
    """
    Validated signal extracted from a webpage.
    """
    category: str = Field(..., description="Category of the signal")
    summary: str = Field(..., min_length=5, description="Plain English summary of the signal")
    evidence: str = Field(..., description="Exact supporting excerpt from source page, max 30 words")
    relevance_score: int = Field(..., ge=0, le=100, description="Relevance score (0-100)")
    urgency_score: int = Field(..., ge=0, le=100, description="Urgency score (0-100)")
    confidence_score: int = Field(..., ge=0, le=100, description="Confidence score (0-100)")
    reasoning: str = Field(..., min_length=5, description="Explanation for assigned scores")
    source_url: str = Field(..., description="Original webpage URL")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        # Match case-insensitively to valid categories
        v_clean = v.strip()
        for cat in VALID_CATEGORIES:
            if v_clean.lower() == cat.lower():
                return cat
        # Default or fallback if slight variance
        if "pain" in v_clean.lower() or "problem" in v_clean.lower():
            return "Pain Points"
        if "demand" in v_clean.lower() or "need" in v_clean.lower():
            return "Demand Signals"
        if "feature" in v_clean.lower() or "request" in v_clean.lower():
            return "Feature Requests"
        if "price" in v_clean.lower() or "cost" in v_clean.lower():
            return "Pricing Concerns"
        if "competitor" in v_clean.lower():
            return "Competitor Activity"
        return "Irrelevant Content"

    @field_validator("evidence")
    @classmethod
    def validate_evidence_length(cls, v: str) -> str:
        v_clean = v.strip().strip('"\'')
        words = re.findall(r"\b\w+\b", v_clean)
        if len(words) > 30:
            # Truncate strictly to first 30 words to comply with max 30 words rule
            v_clean = " ".join(words[:30]) + "..."
        return v_clean


def verify_evidence_in_text(evidence: str, source_text: str) -> bool:
    """
    Verifies that the evidence quote genuinely originates from the source text.
    Handles slight punctuation and whitespace differences.
    """
    if not evidence or not source_text:
        return False

    def normalize(s: str) -> str:
        return re.sub(r"[^\w\s]", "", s.lower())

    norm_ev = normalize(evidence)
    norm_src = normalize(source_text)

    # Check direct substring
    if norm_ev in norm_src:
        return True

    # Token overlap check (at least 75% of sequence tokens appear consecutively or in close proximity)
    ev_tokens = norm_ev.split()
    if len(ev_tokens) <= 3:
        return " ".join(ev_tokens) in norm_src

    # Check 4-word shingles
    shingle_size = min(4, len(ev_tokens))
    shingles = [" ".join(ev_tokens[i:i+shingle_size]) for i in range(len(ev_tokens) - shingle_size + 1)]
    matches = sum(1 for sh in shingles if sh in norm_src)
    return (matches / max(len(shingles), 1)) >= 0.60
