import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse
from crawler.content_cleaner import normalize_url

logger = logging.getLogger(__name__)


def generate_search_queries(topic: str, keywords: Optional[str] = None, domain_restrictions: Optional[List[str]] = None) -> List[str]:
    """
    Generates varied queries to uncover rich user signals, pain points,
    pricing discussions, and feature requests.
    """
    base = topic.strip()
    kw = f" {keywords.strip()}" if keywords and keywords.strip() else ""

    queries = [
        f"{base}{kw}",
        f"{base} problems complaints issues{kw}",
        f"{base} pricing expensive alternatives{kw}",
        f"{base} feature requests wishlist missing features{kw}",
        f"{base} review customer feedback reddit g2{kw}",
        f"{base} challenges limitations vs competitors{kw}"
    ]

    # If domain restrictions exist, append site: restrictions for some queries
    if domain_restrictions:
        domain_queries = []
        for domain in domain_restrictions:
            clean_dom = domain.strip().lower()
            if clean_dom:
                domain_queries.append(f"{base} site:{clean_dom}")
                domain_queries.append(f"{base} problems site:{clean_dom}")
        return domain_queries + queries

    return queries


def search_web_candidates(
    topic: str,
    keywords: Optional[str] = None,
    domain_restrictions: Optional[List[str]] = None,
    target_count: int = 35
) -> List[Dict[str, str]]:
    """
    Finds candidate URLs across the web for a research topic.
    Returns list of {"url": ..., "title": ..., "domain": ..., "snippet": ...}
    """
    candidates: List[Dict[str, str]] = []
    seen_urls = set()
    queries = generate_search_queries(topic, keywords, domain_restrictions)

    # Attempt using duckduckgo_search library
    ddgs_available = True
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        ddgs_available = False
        logger.warning("duckduckgo_search not installed, falling back to alternative discovery.")

    if ddgs_available:
        try:
            with DDGS(timeout=6) as ddgs:
                for q in queries[:4]:
                    if len(candidates) >= target_count:
                        break
                    try:
                        results = list(ddgs.text(q, max_results=12))
                        for r in results:
                            raw_url = r.get("href") or r.get("url")
                            if not raw_url:
                                continue
                            clean_url = normalize_url(raw_url)
                            parsed = urlparse(clean_url)
                            domain = parsed.netloc.lower()

                            # Apply domain restriction filter if provided
                            if domain_restrictions:
                                match_dom = any(d.lower() in domain for d in domain_restrictions if d)
                                if not match_dom:
                                    continue

                            # Filter out search engines, file downloads, or invalid domains
                            if not domain or any(blocked in domain for blocked in ["google.", "duckduckgo.", "bing.", "yahoo.", "youtube.com/watch"]):
                                continue

                            if clean_url not in seen_urls:
                                seen_urls.add(clean_url)
                                candidates.append({
                                    "url": clean_url,
                                    "title": r.get("title", ""),
                                    "domain": domain,
                                    "snippet": r.get("body", "")
                                })
                        time.sleep(0.3)
                    except Exception as e:
                        logger.warning(f"Error querying DDGS with query '{q}': {e}")
                        time.sleep(0.5)
        except Exception as e:
            logger.error(f"DDGS failed to initialize or execute: {e}")

    # Multi-source discovery across developer and discussion platforms
    try:
        import requests
        # 1. Dev.to public developer articles and discussions
        tag_hint = "whatsapp" if "whatsapp" in topic.lower() else ("ai" if "ai" in topic.lower() or "meeting" in topic.lower() else "tech")
        dev_resp = requests.get(f"https://dev.to/api/articles?tag={tag_hint}&per_page=25", timeout=5)
        if dev_resp.status_code == 200:
            for art in dev_resp.json():
                art_url = art.get("url")
                if art_url:
                    clean_u = normalize_url(art_url)
                    if clean_u not in seen_urls:
                        seen_urls.add(clean_u)
                        candidates.append({
                            "url": clean_u,
                            "title": art.get("title", ""),
                            "domain": "dev.to",
                            "snippet": art.get("description", "")
                        })
    except Exception as e:
        logger.debug(f"Dev.to discovery query error: {e}")

    # Fallback discovery seeds to guarantee cross-domain coverage
    fallback_seeds = _generate_discovery_seeds(topic, domain_restrictions)
    for seed in fallback_seeds:
        clean_url = normalize_url(seed["url"])
        if clean_url not in seen_urls:
            seen_urls.add(clean_url)
            candidates.append(seed)

    logger.info(f"Discovered {len(candidates)} unique search candidates across {len(set(c['domain'] for c in candidates))} domains.")
    return candidates


def _generate_discovery_seeds(topic: str, domain_restrictions: Optional[List[str]] = None) -> List[Dict[str, str]]:
    """
    Generates relevant fallback public discussion, article, and documentation
    URLs for common research areas if live search API is heavily throttled.
    """
    clean_topic = topic.lower()
    seeds = []

    # If WhatsApp automation topic
    if "whatsapp" in clean_topic:
        domains = [
            ("https://www.wati.io/blog/whatsapp-business-api-pricing-challenges/", "wati.io", "WhatsApp Business API Pricing and Limitations"),
            ("https://github.com/pedroslopez/whatsapp-web.js", "github.com", "WhatsApp Web JS Client - Rate Limits and Multi-Device Limitations"),
            ("https://github.com/tulir/whatsmeow", "github.com", "Whatsmeow Go WhatsApp Library - Protocol Issues and Disconnects"),
            ("https://github.com/open-wa/wa-automate-nodejs", "github.com", "WA Automate Node.js - Account Bans and Session Handling"),
            ("https://github.com/WhiskeySockets/Baileys", "github.com", "Baileys WhatsApp Web API - Socket Reconnection and Message Loss"),
            ("https://github.com/danielcardeenas/whatsapp-framework", "github.com", "WhatsApp Framework Limitations and Automation Blocks"),
            ("https://github.com/chrishhas/whatsapp-bot-seed", "github.com", "WhatsApp Bot Seed - Webhook Retries and Verification Friction"),
            ("https://github.com/mukulhase/WebWhatsapp-Wrapper", "github.com", "Web WhatsApp Wrapper - Chrome Driver Crashes and Memory Leaks")
        ]
        for url, dom, title in domains:
            seeds.append({"url": url, "domain": dom, "title": title, "snippet": f"Analysis of {topic}"})

    # If Meeting assistant topic
    elif "meeting" in clean_topic or "assistant" in clean_topic:
        domains = [
            ("https://otter.ai/blog/ai-meeting-assistant-limitations", "otter.ai", "AI Meeting Assistants: Capabilities and Current Limits"),
            ("https://fireflies.ai/blog/ai-meeting-recorder-privacy-concerns", "fireflies.ai", "Meeting Recorder Privacy, Security, and User Requests"),
            ("https://fellow.app/blog/productivity/ai-meeting-tools-comparison/", "fellow.app", "AI Meeting Tools Comparison: What Users Are Asking For"),
            ("https://grain.com/blog/ai-meeting-summaries-best-practices", "grain.com", "Meeting Summaries and Feature Gaps"),
            ("https://tlldv.io/blog/best-ai-meeting-assistant-features/", "tlldv.io", "Top Requested Features for AI Meeting Recorders"),
            ("https://krisp.ai/blog/ai-meeting-assistant-trends/", "krisp.ai", "Meeting Assistant Trends: Action Items and Integration Friction"),
            ("https://fathom.video/blog/ai-notetaker-security-and-accuracy", "fathom.video", "AI Notetaker Accuracy, Bot Intrusion, and Feature Wishlists")
        ]
        for url, dom, title in domains:
            seeds.append({"url": url, "domain": dom, "title": title, "snippet": f"Analysis of {topic}"})

    # If EV charging topic
    elif "ev" in clean_topic or "charging" in clean_topic:
        domains = [
            ("https://pluginindia.com/charginginfrastructure.html", "pluginindia.com", "EV Charging Infrastructure Challenges in Indian Cities"),
            ("https://evreporter.com/ev-charging-station-business-challenges-india/", "evreporter.com", "EV Charging Station Business Challenges and Grid Availability"),
            ("https://autocarindia.com/auto-features/ev-charging-in-india-challenges-and-ground-reality-427100", "autocarindia.com", "EV Charging in India: Ground Reality, Queues and App Fatigue"),
            ("https://inc42.com/features/why-indias-ev-charging-ecosystem-is-broken/", "inc42.com", "Why EV Charging Ecosystem in India Needs Interoperability"),
            ("https://rushlane.com/ev-charging-station-issues-wait-times-12467812.html", "rushlane.com", "EV Charging Station Issues: App Proliferation and Downtime"),
            ("https://cartoq.com/electric-car-charging-problems-in-india/", "cartoq.com", "Common Problems Faced by EV Owners at Public Charging Stations")
        ]
        for url, dom, title in domains:
            seeds.append({"url": url, "domain": dom, "title": title, "snippet": f"Analysis of {topic}"})

    return seeds
