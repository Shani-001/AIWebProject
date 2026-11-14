from urllib.parse import urlparse
import streamlit as st
import pandas as pd
from database import db
from exports.export_service import (
    export_findings_to_csv,
    export_findings_to_json,
    generate_one_page_report_markdown
)


def render_findings():
    """Renders the interactive Findings & Evidence Ledger page."""
    st.markdown("## 💡 Findings & Evidence Ledger")
    st.markdown(
        "Explore every verified signal extracted from public web sources. "
        "Filter by category or score threshold, inspect raw quotes, and export structured data."
    )

    sessions = db.get_all_sessions()
    if not sessions:
        st.info("No research findings available yet. Start your first research session to populate findings.")
        return

    # Session Selector
    session_options = {s["id"]: f"#{s['id']} — {s['topic']} ({s['created_at'][:10]})" for s in sessions}
    default_session_id = sessions[0]["id"]

    selected_session_id = st.selectbox(
        "Select Research Session",
        options=list(session_options.keys()),
        format_func=lambda x: session_options[x]
    )

    session = db.get_session_by_id(selected_session_id)
    signals = db.get_signals_for_session(selected_session_id)
    opportunities = db.get_opportunities_for_session(selected_session_id)
    pages = db.get_pages_for_session(selected_session_id)

    if not signals:
        st.warning("No signals found for this research session.")
        return

    # Create mapping of theme name to opportunity score
    theme_score_map = {opp["theme_name"]: opp["opportunity_score"] for opp in opportunities}

    # Add domain and opportunity score into signals for table display
    for s in signals:
        try:
            s["domain"] = urlparse(s.get("page_url", "")).netloc.lower()
        except Exception:
            s["domain"] = "unknown"
        s["opportunity_score"] = theme_score_map.get(s.get("theme_name", ""), 0.0)

    # Filter Controls
    with st.expander("🔍 Filter & Search Findings", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)

        with f_col1:
            all_categories = sorted(list(set(s["category"] for s in signals)))
            selected_categories = st.multiselect(
                "Filter by Category",
                options=all_categories,
                default=all_categories
            )

        with f_col2:
            all_domains = sorted(list(set(s["domain"] for s in signals if s["domain"])))
            selected_domains = st.multiselect(
                "Filter by Domain",
                options=all_domains,
                default=all_domains
            )

        with f_col3:
            search_query = st.text_input("Search Text / Keyword", placeholder="e.g. pricing, integration, bug")

        f_col4, f_col5 = st.columns(2)
        with f_col4:
            min_relevance = st.slider("Minimum Relevance Score", min_value=0, max_value=100, value=0, step=5)
        with f_col5:
            min_opp_score = st.slider("Minimum Opportunity Score", min_value=0.0, max_value=100.0, value=0.0, step=5.0)

    # Apply filters
    filtered_signals = []
    for s in signals:
        if s["category"] not in selected_categories:
            continue
        if selected_domains and s["domain"] not in selected_domains:
            continue
        if s.get("relevance_score", 0) < min_relevance:
            continue
        if s.get("opportunity_score", 0.0) < min_opp_score:
            continue
        if search_query:
            query_match = (
                search_query.lower() in s.get("summary", "").lower() or
                search_query.lower() in s.get("evidence", "").lower() or
                search_query.lower() in s.get("theme_name", "").lower()
            )
            if not query_match:
                continue
        filtered_signals.append(s)

    # Summary count
    st.markdown(f"**Showing {len(filtered_signals)} of {len(signals)} signals** across {len(set(s['domain'] for s in filtered_signals))} domains.")

    # Data table
    if filtered_signals:
        df_display = pd.DataFrame(filtered_signals)[
            ["id", "category", "summary", "theme_name", "relevance_score", "urgency_score", "confidence_score", "opportunity_score", "domain", "page_url"]
        ]
        df_display.columns = ["ID", "Category", "Summary", "Theme", "Relevance", "Urgency", "Confidence", "Opp Score", "Domain", "Source URL"]

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Source URL": st.column_config.LinkColumn("Source URL", display_text="Open Link"),
                "Relevance": st.column_config.ProgressColumn("Relevance", min_value=0, max_value=100, format="%d"),
                "Urgency": st.column_config.ProgressColumn("Urgency", min_value=0, max_value=100, format="%d"),
                "Confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=100, format="%d"),
                "Opp Score": st.column_config.NumberColumn("Opp Score", format="%.1f")
            }
        )

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # Detail View Inspector
        st.subheader("🔎 Signal Detail Inspector")
        signal_ids = [s["id"] for s in filtered_signals]
        selected_sig_id = st.selectbox(
            "Select a signal to inspect verbatim evidence & AI reasoning:",
            options=signal_ids,
            format_func=lambda x: f"Signal #{x}: {next((s['summary'][:80] for s in filtered_signals if s['id'] == x), '')}..."
        )

        selected_sig = next((s for s in filtered_signals if s["id"] == selected_sig_id), None)
        if selected_sig:
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 1.5rem; margin-top: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                        <h4 style="margin: 0; color: #0f172a;">{selected_sig['category']} — {selected_sig.get('theme_name', 'General')}</h4>
                        <span class="tag-badge" style="font-size: 0.85rem;">Opp Score: {selected_sig.get('opportunity_score', 0.0)}</span>
                    </div>
                    <p style="font-size: 1rem; color: #1e293b; margin-bottom: 1rem;">
                        <b>Summary:</b> {selected_sig['summary']}
                    </p>
                    <div style="margin-bottom: 1rem;">
                        <b>Verbatim Supporting Evidence (From Source Webpage):</b>
                        <div class="evidence-quote">
                            "{selected_sig['evidence']}"
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem; background: #f8fafc; padding: 0.75rem; border-radius: 8px;">
                        <div><b>Relevance:</b> {selected_sig['relevance_score']} / 100</div>
                        <div><b>Urgency:</b> {selected_sig['urgency_score']} / 100</div>
                        <div><b>Confidence:</b> {selected_sig['confidence_score']} / 100</div>
                    </div>
                    <p style="font-size: 0.9rem; color: #475569; margin-bottom: 0.75rem;">
                        <b>AI Reasoning:</b> {selected_sig['reasoning']}
                    </p>
                    <div style="font-size: 0.85rem; color: #64748b;">
                        <b>Source URL:</b> <a href="{selected_sig['page_url']}" target="_blank" style="color: #2563eb; text-decoration: none;">{selected_sig['page_url']}</a> |
                        <b>Domain:</b> {selected_sig['domain']} |
                        <b>Evidence Verification:</b> {'✅ Verbatim Verified Source' if selected_sig.get('evidence_verified', 1) else '⚠️ Excerpt Verified'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Export Section
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    st.subheader("📥 Export Intelligence Data")
    st.markdown("Download findings and opportunity reports in standard formats.")

    col_exp1, col_exp2, col_exp3 = st.columns(3)

    csv_data = export_findings_to_csv(filtered_signals)
    with col_exp1:
        st.download_button(
            label="📄 Export Findings (CSV)",
            data=csv_data,
            file_name=f"signals_session_{selected_session_id}.csv",
            mime="text/csv",
            use_container_width=True
        )

    json_data = export_findings_to_json(session, filtered_signals, opportunities)
    with col_exp2:
        st.download_button(
            label="📦 Export All Data (JSON)",
            data=json_data,
            file_name=f"research_session_{selected_session_id}.json",
            mime="application/json",
            use_container_width=True
        )

    unique_domains = list(set(p.get("domain", "") for p in pages if p.get("domain")))
    md_report = generate_one_page_report_markdown(
        session=session,
        opportunities=opportunities,
        pages_count=len(pages),
        domains_covered=unique_domains
    )
    with col_exp3:
        st.download_button(
            label="📑 One-Page Brief Report (Markdown)",
            data=md_report,
            file_name=f"opportunity_brief_report_session_{selected_session_id}.md",
            mime="text/markdown",
            use_container_width=True
        )
