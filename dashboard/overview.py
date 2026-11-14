import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import db


def render_overview():
    """Renders the executive SaaS overview dashboard."""
    metrics = db.get_global_metrics()
    sessions = db.get_all_sessions()
    latest_session = sessions[0] if sessions else None

    # Hero section
    st.markdown(
        """
        <div class="hero-box">
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #0f172a;">
                Discover Hidden Opportunities Across the Web
            </h1>
            <p style="margin: 0.5rem 0 1.25rem 0; font-size: 1.1rem; color: #475569; max-width: 800px;">
                Autonomous web intelligence engine that crawls public discussions, extracts verified market signals,
                and turns unstructured customer feedback into ranked, evidence-backed business opportunities.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Top CTA and quick status
    c_btn, c_info = st.columns([1, 3])
    with c_btn:
        if st.button("🚀 Start New Research", type="primary", use_container_width=True):
            st.session_state["nav_selection"] = "New Research"
            st.rerun()

    with c_info:
        if latest_session:
            st.caption(f"Latest session: **{latest_session['topic']}** ({latest_session['created_at'][:10]}) — {latest_session['status'].upper()}")
        else:
            st.caption("No research sessions recorded yet. Launch a new crawl to begin uncovering opportunities.")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="saas-metric-card">
                <div class="saas-metric-value">{metrics['pages_count']:,}</div>
                <div class="saas-metric-label">Pages Crawled</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class="saas-metric-card">
                <div class="saas-metric-value">{metrics['signals_count']:,}</div>
                <div class="saas-metric-label">Useful Signals Found</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"""
            <div class="saas-metric-card">
                <div class="saas-metric-value">{metrics['opportunities_count']:,}</div>
                <div class="saas-metric-label">Opportunities Discovered</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="saas-metric-card">
                <div class="saas-metric-value">{metrics['sessions_count']:,}</div>
                <div class="saas-metric-label">Sessions Completed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # If no data yet, show friendly guidance
    if not latest_session:
        st.info("💡 Get started by clicking **'Start New Research'** to crawl public discussions and extract verified signals.")
        return

    # Load data for charts
    session_id = latest_session["id"]
    signals = db.get_signals_for_session(session_id)
    opportunities = db.get_opportunities_for_session(session_id)
    pages = db.get_pages_for_session(session_id)

    # Visualizations Row
    st.subheader(f"📊 Market Intelligence: {latest_session['topic']}")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Signal Category Distribution
        if signals:
            df_signals = pd.DataFrame(signals)
            cat_counts = df_signals["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]

            fig_cat = px.pie(
                cat_counts,
                values="Count",
                names="Category",
                hole=0.55,
                title="Signal Category Distribution",
                color_discrete_sequence=["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#f59e0b", "#94a3b8"]
            )
            fig_cat.update_layout(
                margin=dict(t=40, b=20, l=20, r=20),
                legend=dict(orientation="h", y=-0.1),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_cat, use_container_width=True)

    with chart_col2:
        # Top Recurring Themes / Opportunity Scores
        if opportunities:
            df_opps = pd.DataFrame(opportunities)
            df_opps = df_opps.sort_values(by="opportunity_score", ascending=True)

            fig_themes = px.bar(
                df_opps,
                x="opportunity_score",
                y="theme_name",
                orientation="h",
                title="Opportunity Score Comparison (0 - 100)",
                labels={"opportunity_score": "Opportunity Score", "theme_name": "Recurring Theme"},
                color="opportunity_score",
                color_continuous_scale="Blues"
            )
            fig_themes.update_layout(
                margin=dict(t=40, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_themes, use_container_width=True)

    # Domain Coverage and Themes Row
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        if pages:
            df_pages = pd.DataFrame(pages)
            dom_counts = df_pages["domain"].value_counts().head(8).reset_index()
            dom_counts.columns = ["Domain", "Pages"]

            fig_dom = px.bar(
                dom_counts,
                x="Domain",
                y="Pages",
                title="Coverage Across Permitted Domains",
                color="Pages",
                color_continuous_scale="Teal"
            )
            fig_dom.update_layout(
                margin=dict(t=40, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_dom, use_container_width=True)

    with d_col2:
        # Transparent Scoring Formula Explanation Card
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; height: 100%;">
                <h4 style="margin-top: 0; color: #1e3a8a;">📐 Transparent Opportunity Formula</h4>
                <p style="font-size: 0.9rem; color: #475569;">
                    Opportunities are ranked via an audited composite index normalized between 0 and 100:
                </p>
                <div style="background: #f8fafc; padding: 0.75rem; border-radius: 8px; font-family: monospace; font-size: 0.85rem; color: #0f172a; border: 1px solid #e2e8f0;">
                    Score = (0.30 × Relevance) + (0.25 × Urgency) + (0.20 × Confidence) + (0.15 × Frequency) + (0.10 × Recency)
                </div>
                <ul style="font-size: 0.85rem; color: #64748b; margin-top: 0.75rem; padding-left: 1.25rem;">
                    <li><b>Frequency:</b> Multi-source reinforcement across independent web domains.</li>
                    <li><b>Evidence:</b> Direct literal quotes checked against source content.</li>
                    <li><b>Recency:</b> Weighted crawl date recency index.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # Top Five Opportunity Briefs
    st.subheader("🏆 Top Five Discovered Opportunities")
    st.markdown(
        "<p style='color: #64748b; font-size: 0.95rem; margin-top: -0.5rem;'>"
        "Synthesized from real user discussions and evidence quotes. Click source links to verify original text."
        "</p>",
        unsafe_allow_html=True
    )

    if not opportunities:
        st.info("No opportunity briefs generated yet for this session.")
    else:
        for idx, opp in enumerate(opportunities[:5], 1):
            with st.container():
                brief = opp.get("brief_json") or {}
                evidence_items = brief.get("evidence_list", [])

                st.markdown(
                    f"""
                    <div class="opp-card">
                        <div class="opp-header">
                            <div class="opp-title">{idx}. {opp['title']}</div>
                            <div class="opp-score-badge">Score: {opp['opportunity_score']} / 100</div>
                        </div>
                        <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
                            <span class="tag-badge">📚 {opp['source_count']} Independent Sources</span>
                            <span class="tag-badge">🎯 Rel: {opp['avg_relevance']}</span>
                            <span class="tag-badge">⚡ Urg: {opp['avg_urgency']}</span>
                            <span class="tag-badge">🛡️ Conf: {opp['avg_confidence']}</span>
                        </div>
                        <p style="margin: 0.5rem 0; font-size: 0.95rem; color: #334155;">
                            <b>What is happening:</b> {opp['what_is_happening']}
                        </p>
                        <p style="margin: 0.5rem 0; font-size: 0.95rem; color: #334155;">
                            <b>Who has the problem:</b> {opp['who_has_problem']}
                        </p>
                        <p style="margin: 0.5rem 0; font-size: 0.95rem; color: #334155;">
                            <b>Why it matters now:</b> {opp['why_it_matters']}
                        </p>
                        <p style="margin: 0.5rem 0; font-size: 0.95rem; color: #1e3a8a;">
                            <b>Potential Solution:</b> {opp['potential_solution']}
                        </p>
                        <p style="margin: 0.5rem 0; font-size: 0.95rem; color: #047857;">
                            <b>Practical Next Step:</b> {opp['validation_step']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Show supporting evidence quotes with expandable container
                with st.expander(f"🔍 View Supporting Evidence Quotes & Source Links ({len(evidence_items)})"):
                    if evidence_items:
                        for ev in evidence_items:
                            quote_text = ev.get("text", "")
                            quote_url = ev.get("url", "#")
                            st.markdown(
                                f"""
                                <div class="evidence-quote">
                                    "{quote_text}"
                                    <div style="margin-top: 0.25rem; font-size: 0.8rem; font-style: normal;">
                                        🔗 <a href="{quote_url}" target="_blank" style="color: #2563eb; text-decoration: none;">{quote_url}</a>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.caption("Verbatim evidence details stored in findings ledger.")

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Recent Research Activity
    st.subheader("🕒 Recent Research Activity")
    if sessions:
        recent_df = pd.DataFrame(sessions).head(5)[["topic", "ai_provider", "created_at", "pages_crawled_count", "signals_count", "status"]]
        recent_df.columns = ["Topic", "AI Provider", "Date", "Pages", "Signals", "Status"]
        st.dataframe(recent_df, use_container_width=True, hide_index=True)
