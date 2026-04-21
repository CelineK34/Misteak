"""
app.py — FoodAI entry point.
Run with:  streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="FoodAI", layout="wide", page_icon="🍜")

with open("CSS_File/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Register pages ────────────────────────────────────────────────────────────
dashboard  = st.Page("pages/1_dashboard.py",  title="Dashboard",  icon="🏠")
alerts     = st.Page("pages/2_alerts.py",     title="AI Alerts",  icon="🔔")
strategies = st.Page("pages/3_strategies.py", title="Strategies", icon="♟️")
simulator  = st.Page("pages/4_simulator.py",  title="Simulator",  icon="⚙️")
decision   = st.Page("pages/5_decision.py",   title="Decision",   icon="🏆")
settings   = st.Page("pages/6_settings.py",   title="Upload Data",icon="⚡")

pg = st.navigation(
    [dashboard, alerts, strategies, simulator, decision, settings],
    position="hidden",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:20px 8px 16px;">
        <div style="background:#008b5b;border-radius:10px;width:40px;height:40px;
                    display:flex;align-items:center;justify-content:center;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                 stroke="white" stroke-width="2.2" stroke-linecap="round"
                 stroke-linejoin="round">
                <line x1="4" y1="4" x2="20" y2="20"/>
                <line x1="20" y1="4" x2="4" y2="20"/>
                <circle cx="6"  cy="6"  r="2.2"/>
                <circle cx="18" cy="18" r="2.2"/>
            </svg>
        </div>
        <div>
            <div style="font-weight:700;font-size:16px;color:white;letter-spacing:-0.3px;">FoodAI</div>
            <div style="font-size:12px;color:#5ecfa0;">Smart F&B Decisions</div>
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #1a2a1a;margin:0 0 8px 0;">
    <div style="font-size:10px;font-weight:600;color:#334;letter-spacing:0.1em;
                text-transform:uppercase;padding:12px 8px 6px;">Main</div>
    """, unsafe_allow_html=True)

    st.page_link(dashboard,  label="Dashboard",  icon="🏠")
    st.page_link(alerts,     label="AI Alerts",  icon="🔔")
    st.page_link(strategies, label="Strategies", icon="♟️")
    st.page_link(simulator,  label="Simulator",  icon="⚙️")
    st.page_link(decision,   label="Decision",   icon="🏆")

    st.markdown("""
    <div style="font-size:10px;font-weight:600;color:#334;letter-spacing:0.1em;
                text-transform:uppercase;padding:16px 8px 6px;">Settings</div>
    """, unsafe_allow_html=True)
    st.page_link(settings, label="Upload Data", icon="⚡")

    # AI badge at bottom
    st.markdown("""
    <div style="position:fixed;bottom:16px;left:8px;width:218px;
                background:#001f13;border-radius:10px;padding:12px 14px;
                border:1px solid #0d2b1e;">
        <div style="color:#00c47a;font-size:12px;font-weight:600;">
            <span style="display:inline-block;width:8px;height:8px;
                         border-radius:50%;background:#00c47a;
                         margin-right:6px;animation:none;"></span>
            AI-Powered
        </div>
        <div style="color:#4a7a5a;font-size:11px;margin-top:3px;line-height:1.4;">
            Decisions based on your real sales data</div>
    </div>
    """, unsafe_allow_html=True)

pg.run()
