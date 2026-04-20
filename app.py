import streamlit as st

st.set_page_config(page_title="FoodAI", layout="wide", page_icon="🍜")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:20px 8px 16px;">
        <div style="background:#008b5b;border-radius:10px;width:40px;height:40px;
                    display:flex;align-items:center;justify-content:center;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white"
                 stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="4" y1="4" x2="20" y2="20"/>
                <line x1="20" y1="4" x2="4" y2="20"/>
                <circle cx="6" cy="6" r="2"/>
                <circle cx="18" cy="18" r="2"/>
            </svg>
        </div>
        <div>
            <div style="font-weight:700;font-size:16px;color:white;">FoodAI</div>
            <div style="font-size:12px;color:#5ecfa0;">Smart F&B Decisions</div>
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #1e2a1e;margin:0 0 8px 0;">
    """, unsafe_allow_html=True)

    st.page_link("pages/1_dashboard.py", label="Dashboard",   icon="🏠")
    st.page_link("pages/2_Insights.py",  label="AI Alerts",   icon="🔔")
    st.page_link("pages/3_Strategy.py",  label="Strategies",  icon="♟️")
    st.page_link("pages/4_Settings.py",  label="Simulator",   icon="⚙️")
    st.page_link("pages/5_Decision.py",  label="Decision",    icon="🏆")

    st.markdown("""
    <div style="position:fixed;bottom:16px;left:8px;width:218px;
                background:#002e1e;border-radius:10px;padding:10px 14px;">
        <div style="color:#00c47a;font-size:12px;font-weight:600;">AI-Powered</div>
        <div style="color:#5ecfa0;font-size:11px;margin-top:2px;">
            Decisions based on your real sales data</div>
    </div>
    """, unsafe_allow_html=True)

dashboard = st.Page("pages/1_dashboard.py", title="Dashboard",  icon="🏠")
insights  = st.Page("pages/2_Insights.py",  title="AI Alerts",  icon="🔔")
strategy  = st.Page("pages/3_Strategy.py",  title="Strategies", icon="♟️")
settings  = st.Page("pages/4_Settings.py",  title="Simulator",  icon="⚙️")
decision  = st.Page("pages/5_Decision.py",  title="Decision",   icon="🏆")

pg = st.navigation([dashboard, insights, strategy, settings, decision], position="hidden")
pg.run()