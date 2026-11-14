from typing import List, Dict, Any
from config.settings import (
    WEIGHT_RELEVANCE,
    WEIGHT_URGENCY,
    WEIGHT_CONFIDENCE,
    WEIGHT_FREQUENCY,
    WEIGHT_RECENCY
)


def calculate_frequency_score(unique_sources_count: int, target_benchmark: int = 4) -> float:
    """
    Normalizes the frequency of independent sources supporting an opportunity (0 to 100).
    A benchmark of 4 or more distinct sources yields a 100% frequency score.
    """
    if unique_sources_count <= 0:
        return 0.0
    return min(100.0, (unique_sources_count / target_benchmark) * 100.0)


def calculate_opportunity_score(
    avg_relevance: float,
    avg_urgency: float,
    avg_confidence: float,
    frequency_score: float,
    recency_score: float = 100.0
) -> float:
    """
    Calculates the composite opportunity score using the transparent weighted formula:
    Opportunity Score =
        (0.30 * Avg Relevance) +
        (0.25 * Avg Urgency) +
        (0.20 * Avg Confidence) +
        (0.15 * Frequency Score) +
        (0.10 * Recency Score)

    All components are bounded between 0 and 100.
    """
    # Enforce bounds [0, 100]
    rel = max(0.0, min(100.0, avg_relevance))
    urg = max(0.0, min(100.0, avg_urgency))
    conf = max(0.0, min(100.0, avg_confidence))
    freq = max(0.0, min(100.0, frequency_score))
    rec = max(0.0, min(100.0, recency_score))

    score = (
        (WEIGHT_RELEVANCE * rel) +
        (WEIGHT_URGENCY * urg) +
        (WEIGHT_CONFIDENCE * conf) +
        (WEIGHT_FREQUENCY * freq) +
        (WEIGHT_RECENCY * rec)
    )

    return round(score, 1)


def score_theme_signals(signals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes aggregated scores for a list of signals belonging to a single theme.
    """
    if not signals:
        return {
            "avg_relevance": 0.0,
            "avg_urgency": 0.0,
            "avg_confidence": 0.0,
            "frequency_score": 0.0,
            "recency_score": 100.0,
            "opportunity_score": 0.0,
            "source_count": 0,
            "unique_domains": []
        }

    relevance_scores = [s.get("relevance_score", 0) for s in signals]
    urgency_scores = [s.get("urgency_score", 0) for s in signals]
    confidence_scores = [s.get("confidence_score", 0) for s in signals]

    avg_rel = sum(relevance_scores) / len(relevance_scores)
    avg_urg = sum(urgency_scores) / len(urgency_scores)
    avg_conf = sum(confidence_scores) / len(confidence_scores)

    # Count distinct sources / URLs
    source_urls = set(s.get("source_url") for s in signals if s.get("source_url"))
    source_count = len(source_urls)
    freq_score = calculate_frequency_score(source_count)
    rec_score = 100.0  # Live crawl results from today

    opp_score = calculate_opportunity_score(
        avg_relevance=avg_rel,
        avg_urgency=avg_urg,
        avg_confidence=avg_conf,
        frequency_score=freq_score,
        recency_score=rec_score
    )

    return {
        "avg_relevance": round(avg_rel, 1),
        "avg_urgency": round(avg_urg, 1),
        "avg_confidence": round(avg_conf, 1),
        "frequency_score": round(freq_score, 1),
        "recency_score": round(rec_score, 1),
        "opportunity_score": opp_score,
        "source_count": source_count
    }
