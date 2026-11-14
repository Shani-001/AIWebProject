import datetime
import streamlit as st
from config import settings
from crawler.web_crawler import WebCrawlerEngine
from ai_engine.signal_extractor import extract_signal_from_page
from analysis.signal_grouping import group_signals_into_themes
from analysis.opportunity_briefs import generate_opportunity_briefs
from database import db


def render_research():
    """Renders the New Research workflow page."""
    st.markdown("## 🔍 Launch New Research")
    st.markdown(
        "Enter a topic, niche, or business question to crawl live public web discussions, "
        "extract actionable signals with AI, and uncover evidence-backed opportunities."
    )

    # Preset topic suggestions
    st.markdown("**Sample Research Topics:**")
    col_t1, col_t2, col_t3 = st.columns(3)
    preset_topic = None

    with col_t1:
        if st.button("📱 WhatsApp Automation Issues", use_container_width=True):
            preset_topic = "What problems do small businesses mention about WhatsApp automation tools?"
    with col_t2:
        if st.button("🤖 AI Meeting Assistant Features", use_container_width=True):
            preset_topic = "What features are people requesting from AI meeting assistants?"
    with col_t3:
        if st.button("⚡ Pune EV Charging Feedback", use_container_width=True):
            preset_topic = "What demand or complaints appear around EV charging services in Pune?"

    if preset_topic:
        st.session_state["research_topic_input"] = preset_topic

    # Form inputs
    with st.form("research_form"):
        topic = st.text_input(
            "Research Topic or Question *",
            value=st.session_state.get("research_topic_input", ""),
            placeholder="e.g., What problems do small businesses mention about WhatsApp automation tools?",
            help="Specify the core subject, niche, or product domain you want to investigate."
        )

        col_kw, col_prov = st.columns([2, 1])
        with col_kw:
            keywords = st.text_input(
                "Optional Keywords / Focus Phrases",
                placeholder="e.g., pricing, complaints, API limits, integration",
                help="Optional terms to guide search queries and extraction focus."
            )
        with col_prov:
            configured_provider = st.session_state.get("selected_provider", settings.DEFAULT_AI_PROVIDER)
            provider_idx = 0 if configured_provider.lower() == "groq" else 1
            ai_provider = st.selectbox(
                "AI Provider",
                options=["Groq", "Gemini"],
                index=provider_idx,
                help="Choose which LLM provider to use for signal extraction."
            )

        col_pages, col_doms = st.columns([1, 2])
        with col_pages:
            max_pages = st.slider(
                "Maximum Pages to Crawl",
                min_value=5,
                max_value=50,
                value=25,
                step=5,
                help="Target number of public pages to collect across distinct domains."
            )
        with col_doms:
            domain_restrictions_raw = st.text_input(
                "Optional Domain Restrictions (comma-separated)",
                placeholder="e.g., reddit.com, g2.com, trustpilot.com",
                help="Leave blank to search across the open public web."
            )

        submitted = st.form_submit_button("🚀 Start Web Signal Research", type="primary", use_container_width=True)

    if submitted:
        if not topic or not topic.strip():
            st.error("Please enter a research topic or question before starting.")
            return

        domain_restrictions = [d.strip() for d in domain_restrictions_raw.split(",") if d.strip()] if domain_restrictions_raw else None

        # Execute research workflow
        _execute_research_workflow(
            topic=topic.strip(),
            keywords=keywords.strip() if keywords else "",
            ai_provider=ai_provider.lower(),
            max_pages=max_pages,
            domain_restrictions=domain_restrictions
        )


def _execute_research_workflow(topic: str, keywords: str, ai_provider: str, max_pages: int, domain_restrictions):
    """Executes the complete crawl -> extract -> group -> score -> store pipeline."""
    status_box = st.status("Executing Research Workflow...", expanded=True)
    progress_bar = st.progress(0.0)

    # 1. Initialize session
    status_box.write("⚡ Initializing market research session...")
    session_id = db.create_session(
        topic=topic,
        keywords=keywords,
        ai_provider=ai_provider,
        max_pages=max_pages,
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        status="running"
    )

    try:
        # 2. Web Crawling
        status_box.write(f"🌐 Crawling relevant public pages across multiple permitted domains (Target: {max_pages})...")
        crawler = WebCrawlerEngine()

        def crawl_progress(msg, current, total):
            pct = min(0.40, (current / max(total, 1)) * 0.40)
            progress_bar.progress(pct)
            status_box.write(f"  • {msg}")

        crawl_result = crawler.crawl_topic(
            topic=topic,
            keywords=keywords,
            max_pages=max_pages,
            domain_restrictions=domain_restrictions,
            progress_callback=crawl_progress
        )

        crawled_pages = crawl_result["pages"]
        domains_covered = crawl_result["domains_covered"]
        pages_count = len(crawled_pages)

        status_box.write(f"✅ Crawled **{pages_count}** pages across **{len(domains_covered)}** unique domains.")

        if pages_count == 0:
            status_box.update(label="Crawling completed with 0 accessible pages.", state="error")
            db.update_session_summary(session_id, "failed", 0, 0, 0, "No pages could be crawled due to access restrictions or no search matches.")
            st.warning("No accessible pages were retrieved. Please adjust your topic or domain restrictions.")
            return

        # Save crawled pages
        db.save_crawled_pages(session_id, crawled_pages)
        progress_bar.progress(0.45)

        # 3. AI Signal Extraction
        status_box.write(f"🧠 Extracting and validating signals using **{ai_provider.upper()}**...")

        # Retrieve configured API keys from session state or settings
        api_key = None
        if ai_provider == "gemini":
            api_key = st.session_state.get("gemini_api_key") or settings.GEMINI_API_KEY
        else:
            api_key = st.session_state.get("groq_api_key") or settings.GROQ_API_KEY

        signals = []
        for idx, page in enumerate(crawled_pages):
            step_pct = 0.45 + ((idx + 1) / pages_count) * 0.35
            progress_bar.progress(min(0.80, step_pct))

            status_box.write(f"  • Analyzing page {idx+1}/{pages_count}: `{page['domain']}`")
            signal = extract_signal_from_page(
                page=page,
                topic=topic,
                keywords=keywords,
                provider=ai_provider,
                api_key=api_key
            )
            if signal:
                signals.append(signal)

        status_box.write(f"✅ Extracted **{len(signals)}** structured signals.")
        db.save_signals(session_id, signals)
        progress_bar.progress(0.85)

        # 4. Recurring Theme Grouping & Opportunity Ranking
        status_box.write("📈 Grouping signals into recurring themes and computing Opportunity Scores...")
        ranked_themes = group_signals_into_themes(signals, topic=topic)
        progress_bar.progress(0.92)

        # 5. Opportunity Briefs Generation
        status_box.write("📝 Synthesizing Top 5 Opportunity Briefs with verified evidence...")
        briefs = generate_opportunity_briefs(ranked_themes, top_n=5)
        db.save_opportunities(session_id, briefs)
        progress_bar.progress(0.98)

        # 6. Finalize session
        summary_note = (
            f"Successfully crawled {pages_count} pages across {len(domains_covered)} domains. "
            f"Extracted {len(signals)} signals, grouped into {len(ranked_themes)} recurring themes."
        )
        db.update_session_summary(
            session_id=session_id,
            status="completed",
            pages_count=pages_count,
            signals_count=len(signals),
            domains_count=len(domains_covered),
            summary_note=summary_note
        )

        progress_bar.progress(1.0)
        status_box.update(label="🎉 Research Workflow Successfully Completed!", state="complete", expanded=False)

        st.success(f"**Research completed!** Crawled {pages_count} pages across {len(domains_covered)} domains and uncovered {len(briefs)} prioritized opportunities.")

        # Action buttons
        c_act1, c_act2 = st.columns(2)
        with c_act1:
            if st.button("📊 View Opportunities on Dashboard", type="primary", use_container_width=True):
                st.session_state["nav_selection"] = "Dashboard"
                st.rerun()
        with c_act2:
            if st.button("💡 Explore Findings & Evidence Ledger", use_container_width=True):
                st.session_state["nav_selection"] = "Findings"
                st.rerun()

    except Exception as e:
        status_box.update(label=f"Error during workflow: {e}", state="error")
        db.update_session_summary(session_id, "failed", 0, 0, 0, f"Error: {str(e)}")
        st.error(f"Workflow execution encountered an unexpected error: {e}")
