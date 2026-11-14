import streamlit as st
from config import settings
from database.db import init_db
from dashboard.styles import CUSTOM_CSS
from dashboard.overview import render_overview
from dashboard.research import render_research
from dashboard.findings import render_findings
from dashboard.history import render_history
from dashboard.settings import render_settings

# Page configuration
st.set_page_config(
    page_title=f"{settings.APP_TITLE} | {settings.APP_TAGLINE}",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom SaaS styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize database on application boot
init_db()

# Initialize session state for navigation
if "nav_selection" not in st.session_state:
    st.session_state["nav_selection"] = "Dashboard"

# Sidebar Navigation & Branding
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">📡</div>
            <div>
                <div class="sidebar-logo-title">Signal Hunter</div>
                <div class="sidebar-logo-subtitle">Market Intelligence Engine</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    nav_options = [
        "Dashboard",
        "New Research",
        "Findings",
        "Research History",
        "Settings"
    ]

    current_idx = nav_options.index(st.session_state["nav_selection"]) if st.session_state["nav_selection"] in nav_options else 0

    selected_nav = st.radio(
        "Navigation",
        options=nav_options,
        index=current_idx,
        label_visibility="collapsed"
    )

    if selected_nav != st.session_state["nav_selection"]:
        st.session_state["nav_selection"] = selected_nav
        st.rerun()

    # Sleek platform status
    st.markdown(
        """
        <div class="sidebar-status-card">
            <div class="status-indicator-dot"></div>
            <div>
                <div class="status-headline">Intelligence Engine Active</div>
                <div class="status-subline">Ready for Autonomous Discovery</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.caption("AI Web Signal Hunter • Enterprise Intelligence")

# Route to active page
nav = st.session_state["nav_selection"]
if nav == "Dashboard":
    render_overview()
elif nav == "New Research":
    render_research()
elif nav == "Findings":
    render_findings()
elif nav == "Research History":
    render_history()
elif nav == "Settings":
    render_settings()
