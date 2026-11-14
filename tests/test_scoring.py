import pytest
from analysis.opportunity_scoring import calculate_opportunity_score, calculate_frequency_score, score_theme_signals


def test_calculate_opportunity_score_weights():
    # Test formula: (0.30 * 80) + (0.25 * 70) + (0.20 * 90) + (0.15 * 60) + (0.10 * 100)
    # 24 + 17.5 + 18 + 9 + 10 = 78.5
    score = calculate_opportunity_score(
        avg_relevance=80.0,
        avg_urgency=70.0,
        avg_confidence=90.0,
        frequency_score=60.0,
        recency_score=100.0
    )
    assert score == 78.5


def test_calculate_opportunity_score_bounds():
    # Maximum bound 100
    max_score = calculate_opportunity_score(120.0, 150.0, 100.0, 100.0, 100.0)
    assert max_score == 100.0

    # Minimum bound 0
    min_score = calculate_opportunity_score(-10.0, 0.0, 0.0, 0.0, 0.0)
    assert min_score == 0.0


def test_frequency_score_normalization():
    assert calculate_frequency_score(0) == 0.0
    assert calculate_frequency_score(2, target_benchmark=4) == 50.0
    assert calculate_frequency_score(4, target_benchmark=4) == 100.0
    assert calculate_frequency_score(10, target_benchmark=4) == 100.0


def test_score_theme_signals_aggregation():
    sample_signals = [
        {"relevance_score": 90, "urgency_score": 80, "confidence_score": 85, "source_url": "https://a.com/1"},
        {"relevance_score": 80, "urgency_score": 70, "confidence_score": 75, "source_url": "https://b.com/2"}
    ]
    scored = score_theme_signals(sample_signals)
    assert scored["avg_relevance"] == 85.0
    assert scored["avg_urgency"] == 75.0
    assert scored["avg_confidence"] == 80.0
    assert scored["source_count"] == 2
    assert scored["frequency_score"] == 50.0
    assert scored["opportunity_score"] > 0
