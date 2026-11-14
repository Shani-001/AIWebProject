import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from config import settings
from ai_engine.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from ai_engine.validators import SignalItem, verify_evidence_in_text
from ai_engine.groq_client import call_groq_llm
from ai_engine.gemini_client import call_gemini_llm

logger = logging.getLogger(__name__)


def extract_signal_from_page(
    page: Dict[str, Any],
    topic: str,
    keywords: Optional[str] = None,
    provider: str = "groq",
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Analyzes cleaned webpage content to extract a structured signal.
    Validates output with Pydantic and verifies evidence quotes against raw text.
    """
    raw_text = page.get("text_content", "")
    source_url = page.get("url", "")
    page_title = page.get("title", "")

    # Truncate text context to prevent context window overflow while preserving key content
    max_chars = 7000
    cleaned_slice = raw_text[:max_chars] if len(raw_text) > max_chars else raw_text

    user_prompt = USER_PROMPT_TEMPLATE.format(
        topic=topic,
        keywords=keywords or "None",
        source_url=source_url,
        page_title=page_title,
        cleaned_content=cleaned_slice
    )

    # Invoke selected LLM provider
    raw_json = None
    active_provider = provider.lower().strip()

    if active_provider == "gemini":
        raw_json = call_gemini_llm(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT,
            api_key=api_key,
            model=model
        )
    else:
        # Default to Groq
        raw_json = call_groq_llm(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT,
            api_key=api_key,
            model=model
        )

    # If LLM response failed or no API key, fallback to heuristic extraction
    if not raw_json:
        logger.info(f"LLM extraction unavailable for {source_url}, utilizing heuristic verification.")
        return _extract_heuristic_signal(page, topic)

    # Validate with Pydantic
    try:
        # Ensure source_url matches page
        raw_json["source_url"] = source_url
        item = SignalItem(**raw_json)

        # Check evidence verification against source text
        is_verified = verify_evidence_in_text(item.evidence, raw_text)
        if not is_verified:
            logger.warning(f"Evidence from LLM for {source_url} failed exact match verification. Adjusting confidence.")
            # Reduce confidence score if evidence isn't verbatim in crawled text
            item.confidence_score = max(item.confidence_score - 30, 20)
            item.reasoning += " (Note: Evidence excerpt was paraphrased by AI model and did not match verbatim page text)."

        return {
            "category": item.category,
            "summary": item.summary,
            "evidence": item.evidence,
            "relevance_score": item.relevance_score,
            "urgency_score": item.urgency_score,
            "confidence_score": item.confidence_score,
            "reasoning": item.reasoning,
            "source_url": item.source_url,
            "evidence_verified": is_verified,
            "extraction_method": f"LLM ({active_provider.capitalize()})"
        }
    except Exception as e:
        logger.warning(f"Pydantic validation failed for {source_url}: {e}. Falling back to heuristic.")
        return _extract_heuristic_signal(page, topic)


def _extract_heuristic_signal(page: Dict[str, Any], topic: str) -> Optional[Dict[str, Any]]:
    """
    Deterministic NLP/heuristic extractor when LLM key is unconfigured or rate-limited.
    Extracts real verbatim quotes directly from the page text.
    """
    text = page.get("text_content", "")
    source_url = page.get("url", "")
    if not text:
        return None

    # Sentence splitting
    sentences = re.split(r"(?<=[.!?])\s+", text)

    # Keywords for categories
    pain_patterns = ["problem", "difficult", "issue", "bug", "frustrat", "fail", "slow", "down", "error", "limitation"]
    demand_patterns = ["need", "looking for", "require", "demand", "seeking", "must have", "want"]
    feature_patterns = ["feature", "wishlist", "integration", "missing", "request", "support for", "should add"]
    pricing_patterns = ["expensive", "pricing", "cost", "tier", "subscription", "hidden fee", "billing", "per user"]
    competitor_patterns = ["alternative", "switch", "vs", "better than", "compared to", "competitor"]

    best_category = "Irrelevant Content"
    best_sentence = ""
    best_score = 0
    reason = "General information from crawled page."

    for s in sentences:
        s_clean = s.strip()
        words = s_clean.split()
        if len(words) < 5 or len(words) > 40:
            continue
        s_lower = s_clean.lower()

        # Score category matches
        if any(p in s_lower for p in pain_patterns):
            best_category = "Pain Points"
            best_sentence = s_clean
            best_score = 75
            reason = "Mentions technical difficulty, friction, or limitations experienced by users."
            break
        elif any(p in s_lower for p in pricing_patterns):
            best_category = "Pricing Concerns"
            best_sentence = s_clean
            best_score = 70
            reason = "Discusses pricing models, costs, or affordability challenges."
            break
        elif any(p in s_lower for p in feature_patterns):
            best_category = "Feature Requests"
            best_sentence = s_clean
            best_score = 72
            reason = "Highlights missing capabilities or feature desires."
            break
        elif any(p in s_lower for p in demand_patterns):
            best_category = "Demand Signals"
            best_sentence = s_clean
            best_score = 68
            reason = "Shows active need or requirement for specific tools/capabilities."
            break
        elif any(p in s_lower for p in competitor_patterns):
            best_category = "Competitor Activity"
            best_sentence = s_clean
            best_score = 65
            reason = "Compares solutions and market alternatives."
            break

    # If no strong category found
    if best_category == "Irrelevant Content" or not best_sentence:
        # Use first meaningful sentence if relevant
        first_meaningful = next((s for s in sentences if len(s.split()) >= 6), "")
        best_sentence = first_meaningful[:120] if first_meaningful else f"Discussion regarding {topic}."
        best_score = 30
        best_category = "Irrelevant Content"
        reason = "Page contains background information but lacks strong actionable market signals."

    # Enforce max 30 words for evidence
    words = best_sentence.split()
    evidence_quote = " ".join(words[:28]) if len(words) > 28 else best_sentence

    summary = f"{best_category} identified regarding {topic} in discussions on {page.get('domain', '')}."

    return {
        "category": best_category,
        "summary": summary,
        "evidence": evidence_quote,
        "relevance_score": best_score,
        "urgency_score": max(best_score - 10, 20),
        "confidence_score": 75,
        "reasoning": f"Extracted directly from page content: {reason}",
        "source_url": source_url,
        "evidence_verified": True,
        "extraction_method": "NLP Pattern Engine"
    }
