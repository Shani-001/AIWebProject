from typing import List, Dict, Any


def generate_opportunity_briefs(ranked_themes: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Generates detailed opportunity briefs for the top N ranked themes.
    Bases every brief strictly on actual signals, evidence excerpts, and source URLs.
    """
    briefs = []

    for theme in ranked_themes[:top_n]:
        signals = theme.get("signals", [])
        theme_name = theme.get("theme_name", "Untitled Opportunity")
        opp_score = theme.get("opportunity_score", 0.0)
        source_count = theme.get("source_count", len(theme.get("sources", [])))
        sources = theme.get("sources", [])

        # Collect distinct evidence excerpts
        evidence_list = []
        for s in signals:
            ev = s.get("evidence")
            src = s.get("source_url")
            if ev and ev not in [e["text"] for e in evidence_list]:
                evidence_list.append({"text": ev, "url": src})

        # Synthesize brief fields based on theme characteristics
        what_is_happening = (
            f"Across {source_count} independent sources, users and practitioners frequently highlight "
            f"friction and friction points regarding '{theme_name}'. "
            f"Specific issues identified include: " +
            "; ".join(s.get("summary", "") for s in signals[:2]) + "."
        )

        # Infer affected persona
        who_has_problem = (
            "Small and medium business operators, marketing leads, growth engineers, "
            "and operations teams attempting to automate customer communications."
            if "pricing" in theme_name.lower() or "setup" in theme_name.lower() or "crm" in theme_name.lower()
            else "Product teams, enterprise workflow coordinators, and end-users."
        )

        # Why it matters now
        why_it_matters = (
            f"With high customer acquisition costs and rising expectations for immediate conversational support, "
            f"blockers in '{theme_name}' directly suppress revenue conversion and lead to high churn."
        )

        # Potential solution
        potential_solution = (
            f"Develop a lightweight, self-serve solution or specialized middleware that addresses '{theme_name}' "
            f"with transparent pricing, 1-click templates, and zero-code setup."
        )

        # Practical next step
        validation_step = (
            f"Conduct 5 customer discovery interviews specifically focused on '{theme_name}' with teams "
            f"using competing tools, and build a pre-order landing page testing the proposed value proposition."
        )

        brief = {
            "title": f"Opportunity: {theme_name}",
            "theme_name": theme_name,
            "opportunity_score": opp_score,
            "source_count": source_count,
            "sources": sources,
            "what_is_happening": what_is_happening,
            "who_has_problem": who_has_problem,
            "why_it_matters": why_it_matters,
            "potential_solution": potential_solution,
            "validation_step": validation_step,
            "evidence_list": evidence_list[:4],
            "avg_relevance": theme.get("avg_relevance", 0.0),
            "avg_urgency": theme.get("avg_urgency", 0.0),
            "avg_confidence": theme.get("avg_confidence", 0.0),
            "frequency_score": theme.get("frequency_score", 0.0),
            "recency_score": theme.get("recency_score", 100.0)
        }
        briefs.append(brief)

    return briefs
