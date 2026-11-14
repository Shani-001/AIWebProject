"""Custom CSS styles for modern SaaS UI/UX design."""

CUSTOM_CSS = """
<style>
/* Global resets & typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #0f172a;
}

/* Main block container */
.main .block-container {
    padding-top: 1.75rem;
    padding-bottom: 3.5rem;
    max-width: 1240px;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
    padding-left: 1.25rem;
    padding-right: 1.25rem;
}

/* Sidebar branding header */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid #f1f5f9;
    margin-bottom: 1.25rem;
}
.sidebar-logo-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: #ffffff;
    font-size: 1.25rem;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
}
.sidebar-logo-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.15;
    letter-spacing: -0.01em;
}
.sidebar-logo-subtitle {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 500;
}

/* Sidebar status pill */
.sidebar-status-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-top: 1.5rem;
}
.status-indicator-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #10b981;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
    70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}
.status-headline {
    font-size: 0.825rem;
    font-weight: 600;
    color: #1e293b;
    line-height: 1.2;
}
.status-subline {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.15rem;
}

/* Hero Section */
.hero-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 2.25rem 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.02), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
    position: relative;
    overflow: hidden;
}
.hero-box::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #2563eb 0%, #3b82f6 50%, #60a5fa 100%);
}
.hero-title {
    margin: 0;
    font-size: 2.1rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.025em;
    line-height: 1.2;
}
.hero-desc {
    margin: 0.75rem 0 0 0;
    font-size: 1.05rem;
    color: #475569;
    max-width: 820px;
    line-height: 1.6;
}

/* Metric Cards */
.saas-metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.4rem 1.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03);
    transition: all 0.2s ease-in-out;
    position: relative;
    overflow: hidden;
}
.saas-metric-card:hover {
    border-color: #cbd5e1;
    transform: translateY(-2px);
    box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.05);
}
.saas-metric-value {
    font-size: 2.25rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
    letter-spacing: -0.03em;
}
.saas-metric-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #64748b;
    margin-top: 0.35rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* Opportunity Brief Cards */
.opp-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.75rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    transition: border-color 0.2s ease;
}
.opp-card:hover {
    border-color: #cbd5e1;
}
.opp-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.85rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}
.opp-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.01em;
}
.opp-score-badge {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #dbeafe;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 0.875rem;
    letter-spacing: -0.01em;
}

/* Badge tags */
.tag-badge {
    display: inline-flex;
    align-items: center;
    background: #f1f5f9;
    color: #334155;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
    font-size: 0.775rem;
    font-weight: 600;
    margin-right: 0.4rem;
}

/* Evidence quote boxes */
.evidence-quote {
    background: #f8fafc;
    border-left: 3px solid #2563eb;
    padding: 0.85rem 1.15rem;
    margin: 0.65rem 0;
    font-style: italic;
    color: #1e293b;
    border-radius: 0 8px 8px 0;
    font-size: 0.925rem;
    line-height: 1.5;
}

/* Surface containers */
.surface-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

/* Hide default streamlit clutter */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
