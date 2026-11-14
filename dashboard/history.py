import streamlit as st
import pandas as pd
from database import db
from exports.export_service import generate_one_page_report_markdown


def render_history():
    """Renders the historical research sessions archive and comparison view."""
    st.markdown("## 📜 Research Session Archive")
    st.markdown("Review past web signal research runs, compare findings across topics, and manage historical datasets.")

    sessions = db.get_all_sessions()
    if not sessions:
        st.info("No prior research sessions recorded yet.")
        return

    # Primary Sessions Ledger Table
    df_sessions = pd.DataFrame(sessions)[
        ["id", "topic", "keywords", "ai_provider", "pages_crawled_count", "signals_count", "domains_count", "created_at", "status"]
    ]
    df_sessions.columns = ["ID", "Topic", "Keywords", "AI Provider", "Pages", "Signals", "Domains", "Date", "Status"]

    st.dataframe(
        df_sessions,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Pages": st.column_config.NumberColumn("Pages"),
            "Signals": st.column_config.NumberColumn("Signals"),
            "Domains": st.column_config.NumberColumn("Domains"),
        }
    )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Historical Session Actions & Inspector
    st.subheader("⚙️ Session Inspector & Management")
    col_sel, col_del = st.columns([3, 1])

    with col_sel:
        session_map = {s["id"]: f"#{s['id']} — {s['topic']} ({s['created_at'][:10]})" for s in sessions}
        selected_id = st.selectbox("Choose Session to Inspect:", options=list(session_map.keys()), format_func=lambda x: session_map[x])

    with col_del:
        st.markdown("<div style='height: 1.7rem;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Delete Session", type="secondary", use_container_width=True):
            db.delete_session(selected_id)
            st.success(f"Session #{selected_id} deleted successfully.")
            st.rerun()

    selected_session = db.get_session_by_id(selected_id)
    opps = db.get_opportunities_for_session(selected_id)
    pages = db.get_pages_for_session(selected_id)
    signals = db.get_signals_for_session(selected_id)

    if selected_session:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; margin-top: 1rem;">
                <h4 style="margin: 0; color: #1e3a8a;">#{selected_session['id']}: {selected_session['topic']}</h4>
                <p style="margin: 0.5rem 0; color: #475569; font-size: 0.95rem;">
                    <b>Summary Note:</b> {selected_session.get('summary_note', 'N/A')}
                </p>
                <div style="display: flex; gap: 1rem; font-size: 0.85rem; color: #64748b;">
                    <span><b>Pages Crawled:</b> {selected_session['pages_crawled_count']}</span>
                    <span><b>Signals Found:</b> {selected_session['signals_count']}</span>
                    <span><b>Domains:</b> {selected_session['domains_count']}</span>
                    <span><b>Provider:</b> {selected_session['ai_provider'].upper()}</span>
                    <span><b>Status:</b> {selected_session['status']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Quick Actions
        c_open, c_report = st.columns(2)
        with c_open:
            if st.button("💡 Open Findings for this Session", use_container_width=True):
                st.session_state["nav_selection"] = "Findings"
                st.rerun()

        with c_report:
            domains_list = list(set(p["domain"] for p in pages if p.get("domain")))
            report_text = generate_one_page_report_markdown(selected_session, opps, len(pages), domains_list)
            st.download_button(
                label="📄 Download Executive Report (.md)",
                data=report_text,
                file_name=f"executive_report_session_{selected_id}.md",
                mime="text/markdown",
                use_container_width=True
            )

    # Session Comparison Tool
    if len(sessions) >= 2:
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        st.subheader("⚖️ Compare Two Research Sessions")

        c_cmp1, c_cmp2 = st.columns(2)
        with c_cmp1:
            id_a = st.selectbox("Select Session A:", options=list(session_map.keys()), index=0, key="cmp_a")
        with c_cmp2:
            id_b = st.selectbox("Select Session B:", options=list(session_map.keys()), index=min(1, len(sessions)-1), key="cmp_b")

        if id_a != id_b:
            sess_a = db.get_session_by_id(id_a)
            sess_b = db.get_session_by_id(id_b)
            opps_a = db.get_opportunities_for_session(id_a)
            opps_b = db.get_opportunities_for_session(id_b)

            col_a_view, col_b_view = st.columns(2)
            with col_a_view:
                st.markdown(f"#### Session #{id_a}: {sess_a['topic']}")
                st.markdown(f"- **Provider:** {sess_a['ai_provider'].upper()}")
                st.markdown(f"- **Pages Crawled:** {sess_a['pages_crawled_count']}")
                st.markdown(f"- **Useful Signals:** {sess_a['signals_count']}")
                st.markdown("**Top Discovered Opportunities:**")
                for o in opps_a[:3]:
                    st.markdown(f"- **{o['title']}** (Score: {o['opportunity_score']})")

            with col_b_view:
                st.markdown(f"#### Session #{id_b}: {sess_b['topic']}")
                st.markdown(f"- **Provider:** {sess_b['ai_provider'].upper()}")
                st.markdown(f"- **Pages Crawled:** {sess_b['pages_crawled_count']}")
                st.markdown(f"- **Useful Signals:** {sess_b['signals_count']}")
                st.markdown("**Top Discovered Opportunities:**")
                for o in opps_b[:3]:
                    st.markdown(f"- **{o['title']}** (Score: {o['opportunity_score']})")
