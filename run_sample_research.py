"""
Sample Research Runner
Executes an end-to-end research session on:
'What problems do small businesses mention about WhatsApp automation tools?'
Crawling at least 25 relevant pages across at least 3 permitted domains.
"""
import sys
import datetime
from crawler.web_crawler import WebCrawlerEngine
from ai_engine.signal_extractor import extract_signal_from_page
from analysis.signal_grouping import group_signals_into_themes
from analysis.opportunity_briefs import generate_opportunity_briefs
from database import db
from config import settings


def main():
    print("=" * 70)
    print("AI WEB SIGNAL HUNTER - SAMPLE RESEARCH WORKFLOW")
    print("=" * 70)

    db.init_db()

    topic = "What problems do small businesses mention about WhatsApp automation tools?"
    keywords = "pricing, template approval, CRM integration, account bans, complexity"
    ai_provider = "groq"
    max_pages = 25

    print(f"\n[1/5] Initializing session in SQLite...")
    session_id = db.create_session(
        topic=topic,
        keywords=keywords,
        ai_provider=ai_provider,
        max_pages=max_pages,
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        status="running"
    )
    print(f"Session ID: {session_id}")

    print(f"\n[2/5] Crawling at least {max_pages} public pages across at least 3 domains...")
    crawler = WebCrawlerEngine(delay=0.4)

    def progress(msg, cur, tot):
        print(f"   --> {msg}", flush=True)

    crawl_result = crawler.crawl_topic(
        topic=topic,
        keywords=keywords,
        max_pages=max_pages,
        progress_callback=progress
    )

    pages = crawl_result["pages"]
    domains = crawl_result["domains_covered"]
    print(f" Crawled: {len(pages)} pages across {len(domains)} domains.")
    print(f" Domains: {', '.join(domains[:5])}...")

    # Save pages
    db.save_crawled_pages(session_id, pages)

    print(f"\n[3/5] Extracting signals from crawled pages with validation...")
    signals = []
    for idx, page in enumerate(pages):
        sys.stdout.write(f"\r   Processing page {idx+1}/{len(pages)}: {page['domain'][:25]}")
        sys.stdout.flush()
        sig = extract_signal_from_page(
            page=page,
            topic=topic,
            keywords=keywords,
            provider=ai_provider
        )
        if sig:
            signals.append(sig)
    print(f"\n Extracted {len(signals)} structured signals.")
    db.save_signals(session_id, signals)

    print(f"\n[4/5] Grouping recurring themes and calculating Opportunity Scores...")
    ranked_themes = group_signals_into_themes(signals, topic=topic)
    print(f" Discovered {len(ranked_themes)} recurring opportunity themes.")

    print(f"\n[5/5] Synthesizing Top 5 Opportunity Briefs with verified evidence...")
    briefs = generate_opportunity_briefs(ranked_themes, top_n=5)
    db.save_opportunities(session_id, briefs)

    # Finalize session
    summary_note = (
        f"Completed crawl of {len(pages)} pages across {len(domains)} domains. "
        f"Identified {len(signals)} verified signals and {len(briefs)} opportunity briefs."
    )
    db.update_session_summary(
        session_id=session_id,
        status="completed",
        pages_count=len(pages),
        signals_count=len(signals),
        domains_count=len(domains),
        summary_note=summary_note
    )

    print("\n" + "=" * 70)
    print("TOP FIVE DISCOVERED OPPORTUNITIES:")
    print("=" * 70)
    for idx, b in enumerate(briefs, 1):
        print(f"\n{idx}. {b['title']}")
        print(f"   Opportunity Score: {b['opportunity_score']} / 100")
        print(f"   Sources: {b['source_count']} independent sources")
        print(f"   What is happening: {b['what_is_happening'][:120]}...")
        print(f"   Solution Angle: {b['potential_solution'][:120]}...")
        if b.get("evidence_list"):
            first_ev = b["evidence_list"][0]
            print(f"   Evidence Excerpt: \"{first_ev.get('text', '')[:100]}\"")
            print(f"   Source URL: {first_ev.get('url', '')}")

    print("\nSample research workflow completed successfully and saved to SQLite!")


if __name__ == "__main__":
    main()
