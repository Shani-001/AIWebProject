import os
import streamlit as st
from config import settings
from ai_engine.groq_client import call_groq_llm
from ai_engine.gemini_client import call_gemini_llm


def render_settings():
    """Renders the Settings & API Configuration page."""
    st.markdown("## ⚙️ Settings & API Configuration")
    st.markdown(
        "Configure your AI model providers, API credentials, and default crawler parameters. "
        "Credentials are kept secure and never exposed publicly."
    )

    # API Keys Section
    st.subheader("🔑 AI Provider Credentials")

    current_groq_key = st.session_state.get("groq_api_key", settings.GROQ_API_KEY)
    current_gemini_key = st.session_state.get("gemini_api_key", settings.GEMINI_API_KEY)
    current_provider = st.session_state.get("selected_provider", settings.DEFAULT_AI_PROVIDER)

    with st.form("settings_form"):
        st.markdown("#### Groq Configuration")
        groq_key_input = st.text_input(
            "Groq API Key",
            value=current_groq_key,
            type="password",
            placeholder="gsk_...",
            help="Required for Llama 3.3 high-speed inference. Get key from console.groq.com."
        )

        st.markdown("#### Google Gemini Configuration")
        gemini_key_input = st.text_input(
            "Gemini API Key",
            value=current_gemini_key,
            type="password",
            placeholder="AIzaSy...",
            help="Required for Gemini 1.5 Flash analysis. Get key from aistudio.google.com."
        )

        st.markdown("#### Defaults")
        col_p, col_c = st.columns(2)
        with col_p:
            provider_idx = 0 if current_provider.lower() == "groq" else 1
            default_provider = st.selectbox(
                "Default AI Provider",
                options=["Groq", "Gemini"],
                index=provider_idx
            )
        with col_c:
            default_max_pages = st.number_input(
                "Default Maximum Pages per Session",
                min_value=5,
                max_value=100,
                value=settings.MAX_PAGES_DEFAULT,
                step=5
            )

        save_btn = st.form_submit_button("💾 Save Settings", type="primary")

    if save_btn:
        st.session_state["groq_api_key"] = groq_key_input.strip()
        st.session_state["gemini_api_key"] = gemini_key_input.strip()
        st.session_state["selected_provider"] = default_provider.lower()
        st.session_state["default_max_pages"] = default_max_pages

        # Persist to local .env if possible
        try:
            env_file = settings.BASE_DIR / ".env"
            env_content = f"""# AI Web Signal Hunter - Auto-saved Configuration
DEFAULT_AI_PROVIDER={default_provider.lower()}
GROQ_API_KEY={groq_key_input.strip()}
GROQ_MODEL={settings.GROQ_MODEL}
GEMINI_API_KEY={gemini_key_input.strip()}
GEMINI_MODEL={settings.GEMINI_MODEL}
MAX_PAGES_DEFAULT={default_max_pages}
CRAWL_TIMEOUT_SECONDS={settings.CRAWL_TIMEOUT_SECONDS}
CRAWL_DELAY_SECONDS={settings.CRAWL_DELAY_SECONDS}
USER_AGENT={settings.USER_AGENT}
"""
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(env_content)
            st.success("Settings saved to active session and .env configuration file!")
        except Exception as e:
            st.success("Settings updated in current runtime session.")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Connection Diagnostics / Test Section
    st.subheader("🧪 Test AI Provider Connections")
    col_t_groq, col_t_gem = st.columns(2)

    with col_t_groq:
        if st.button("Test Groq Connection", use_container_width=True):
            test_key = st.session_state.get("groq_api_key") or settings.GROQ_API_KEY
            if not test_key:
                st.error("No Groq API key entered.")
            else:
                with st.spinner("Pinging Groq API..."):
                    res = call_groq_llm(
                        prompt="Respond with JSON: {\"status\": \"ok\", \"ping\": true}",
                        system_prompt="You are a health check assistant. Respond only with JSON.",
                        api_key=test_key,
                        max_retries=1
                    )
                    if res and res.get("status") == "ok":
                        st.success("✅ Groq API connection verified successfully!")
                    else:
                        st.error("❌ Groq API test failed. Check key validity and network.")

    with col_t_gem:
        if st.button("Test Gemini Connection", use_container_width=True):
            test_key = st.session_state.get("gemini_api_key") or settings.GEMINI_API_KEY
            if not test_key:
                st.error("No Gemini API key entered.")
            else:
                with st.spinner("Pinging Gemini API..."):
                    res = call_gemini_llm(
                        prompt="Respond with JSON: {\"status\": \"ok\", \"ping\": true}",
                        system_prompt="You are a health check assistant. Respond only with JSON.",
                        api_key=test_key,
                        max_retries=1
                    )
                    if res and res.get("status") == "ok":
                        st.success("✅ Gemini API connection verified successfully!")
                    else:
                        st.error("❌ Gemini API test failed. Check key validity and network.")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Privacy & Access Notice
    st.markdown(
        """
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.15rem; font-size: 0.85rem; color: #64748b; line-height: 1.5;">
            <b style="color: #334155;">Compliance & Privacy Notice:</b> AI Web Signal Hunter honors public domain access rules,
            responsible web crawling standards, and polite traffic rate limits. All API credentials and research results remain entirely private on your system.
        </div>
        """,
        unsafe_allow_html=True
    )
