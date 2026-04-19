import streamlit as st

st.set_page_config(page_title="FoodAI", layout="wide", page_icon="🍜")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:20px 8px 16px;">
        <div style="background:#16a34a;border-radius:10px;width:40px;height:40px;
                    display:flex;align-items:center;justify-content:center;font-size:20px;">🍜</div>
        <div>
            <div style="font-weight:700;font-size:16px;color:white;">FoodAI</div>
            <div style="font-size:12px;color:#6ee7b7;">Smart F&B Decisions</div>
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #1e3a2a;margin:0 0 12px 0;">
    """, unsafe_allow_html=True)

    st.page_link("pages/1_Dashboard.py",  label="Dashboard",   icon="🏠")
    st.page_link("pages/2_Insights.py",   label="AI Insights", icon="🧠")
    st.page_link("pages/3_Strategy.py",   label="Strategy",    icon="♟️")
    st.page_link("pages/4_Settings.py",   label="Settings",    icon="⚙️")

    st.markdown("""
    <div style="position:fixed;bottom:16px;left:8px;width:210px;
                background:#0f2d1f;border-radius:10px;padding:10px 14px;">
        <div style="color:#4ade80;font-size:12px;font-weight:600;">AI-Powered</div>
        <div style="color:#6ee7b7;font-size:11px;margin-top:2px;">
            Decisions based on your real sales data</div>
    </div>
    """, unsafe_allow_html=True)

dashboard = st.Page("pages/1_Dashboard.py", title="Dashboard",   icon="🏠")
insights  = st.Page("pages/2_Insights.py",  title="AI Insights", icon="🧠")
strategy  = st.Page("pages/3_Strategy.py",  title="Strategy",    icon="♟️")
settings  = st.Page("pages/4_Settings.py",  title="Settings",    icon="⚙️")

pg = st.navigation([dashboard, insights, strategy, settings], position="hidden")
pg.run()