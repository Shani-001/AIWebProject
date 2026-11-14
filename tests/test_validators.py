import pytest
from pydantic import ValidationError
from ai_engine.validators import SignalItem, verify_evidence_in_text


def test_valid_signal_item():
    item = SignalItem(
        category="Pain Points",
        summary="Users find CRM integration with WhatsApp excessively difficult.",
        evidence="Connecting WhatsApp API to HubSpot requires complex custom webhooks.",
        relevance_score=85,
        urgency_score=75,
        confidence_score=90,
        reasoning="Explicit mention of technical integration blocker.",
        source_url="https://respond.io/blog/whatsapp-problems"
    )
    assert item.category == "Pain Points"
    assert item.relevance_score == 85
    assert len(item.evidence.split()) <= 30


def test_signal_item_category_fallback():
    item = SignalItem(
        category="customer problem with price",
        summary="Subscription tiers are prohibitively costly for solo founders.",
        evidence="The starter plan begins at 99 dollars per month.",
        relevance_score=70,
        urgency_score=60,
        confidence_score=80,
        reasoning="Mentions high entry cost.",
        source_url="https://wati.io/pricing"
    )
    assert item.category in ["Pain Points", "Pricing Concerns"]


def test_evidence_truncation_to_max_30_words():
    long_evidence = " ".join(["word"] * 45)
    item = SignalItem(
        category="Feature Requests",
        summary="Users desire native calendar scheduling within chat sessions.",
        evidence=long_evidence,
        relevance_score=80,
        urgency_score=60,
        confidence_score=70,
        reasoning="Requested feature wishlist.",
        source_url="https://example.com"
    )
    words = item.evidence.split()
    assert len(words) <= 31  # 30 words + ellipsis


def test_verify_evidence_in_text():
    page_text = (
        "Many small companies report that the WhatsApp Business API verification process "
        "takes upwards of two weeks and often gets rejected without clear explanations."
    )
    real_quote = "WhatsApp Business API verification process takes upwards of two weeks"
    fake_quote = "WhatsApp completely banned our entire marketing department yesterday"

    assert verify_evidence_in_text(real_quote, page_text) is True
    assert verify_evidence_in_text(fake_quote, page_text) is False


def test_invalid_score_raises_validation_error():
    with pytest.raises(ValidationError):
        SignalItem(
            category="Pain Points",
            summary="A short summary",
            evidence="Short quote",
            relevance_score=150,  # Invalid: > 100
            urgency_score=50,
            confidence_score=50,
            reasoning="Some reasoning",
            source_url="https://example.com"
        )
