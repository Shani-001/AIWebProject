import re
from typing import List, Dict, Any
from collections import defaultdict
from analysis.opportunity_scoring import score_theme_signals


THEME_RULES = [
    {
        "name": "Integration & CRM Sync Barriers",
        "keywords": ["integration", "crm", "hubspot", "salesforce", "webhook", "api", "sync", "connect", "export"],
        "category_affinity": ["Pain Points", "Feature Requests"]
    },
    {
        "name": "High Pricing & Hidden Tier Costs",
        "keywords": ["pricing", "price", "expensive", "cost", "tier", "subscription", "per user", "markup", "billing", "unaffordable"],
        "category_affinity": ["Pricing Concerns", "Pain Points"]
    },
    {
        "name": "Setup Complexity & Onboarding Friction",
        "keywords": ["setup", "difficult", "complicated", "complex", "configuration", "learning curve", "confusing", "hard to", "onboarding"],
        "category_affinity": ["Pain Points"]
    },
    {
        "name": "Template Verification & Compliance Hurdles",
        "keywords": ["template", "approval", "compliance", "verification", "meta", "ban", "blocked", "policy", "reject"],
        "category_affinity": ["Pain Points"]
    },
    {
        "name": "Customer Support & Downtime Issues",
        "keywords": ["support", "unresponsive", "downtime", "slow", "bug", "glitch", "crash", "outage", "ticket", "service"],
        "category_affinity": ["Pain Points", "Competitor Activity"]
    },
    {
        "name": "Analytics, Reporting & Transparency Gaps",
        "keywords": ["analytics", "report", "dashboard", "metrics", "insights", "tracking", "visibility", "roi", "data"],
        "category_affinity": ["Feature Requests", "Demand Signals"]
    },
    {
        "name": "High Intent for AI-Driven Automation",
        "keywords": ["ai", "automation", "workflow", "bot", "auto", "smart", "assist", "agent", "automate", "efficiency"],
        "category_affinity": ["Demand Signals", "Feature Requests"]
    },
    {
        "name": "Competitive Migration & Vendor Lock-in",
        "keywords": ["alternative", "switch", "migrate", "competitor", "vs", "lock-in", "churn", "better than"],
        "category_affinity": ["Competitor Activity", "Demand Signals"]
    }
]


def group_signals_into_themes(signals: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
    """
    Groups extracted signals into coherent recurring themes.
    Computes scores for each theme and ranks them.
    """
    if not signals:
        return []

    # Map signals to themes
    theme_buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    unassigned: List[Dict[str, Any]] = []

    for signal in signals:
        # Ignore irrelevant signals in core opportunity themes
        if signal.get("category") == "Irrelevant Content":
            continue

        text_to_check = f"{signal.get('summary', '')} {signal.get('evidence', '')} {signal.get('reasoning', '')}".lower()
        matched_theme = None

        for rule in THEME_RULES:
            match_count = sum(1 for kw in rule["keywords"] if re.search(r"\b" + re.escape(kw) + r"\b", text_to_check))
            cat_match = signal.get("category") in rule["category_affinity"]
            if match_count >= 1 and cat_match:
                matched_theme = rule["name"]
                break
            elif match_count >= 2:
                matched_theme = rule["name"]
                break

        if matched_theme:
            signal["theme_name"] = matched_theme
            theme_buckets[matched_theme].append(signal)
        else:
            unassigned.append(signal)

    # Distribute unassigned signals into dynamic category themes if any
    for sig in unassigned:
        fallback_theme = f"General {sig.get('category', 'Market Signal')} in {topic[:25]}"
        sig["theme_name"] = fallback_theme
        theme_buckets[fallback_theme].append(sig)

    # Score each theme
    ranked_themes = []
    for theme_name, theme_signals in theme_buckets.items():
        if not theme_signals:
            continue

        scores = score_theme_signals(theme_signals)

        ranked_themes.append({
            "theme_name": theme_name,
            "topic": topic,
            "signal_count": len(theme_signals),
            "signals": theme_signals,
            "opportunity_score": scores["opportunity_score"],
            "avg_relevance": scores["avg_relevance"],
            "avg_urgency": scores["avg_urgency"],
            "avg_confidence": scores["avg_confidence"],
            "frequency_score": scores["frequency_score"],
            "recency_score": scores["recency_score"],
            "source_count": scores["source_count"],
            "sources": list(set(s.get("source_url") for s in theme_signals if s.get("source_url")))
        })

    # Sort themes strictly descending by Opportunity Score
    ranked_themes.sort(key=lambda t: t["opportunity_score"], reverse=True)

    return ranked_themes
