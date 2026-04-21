"""
pages/2_alerts.py — AI-generated alerts and opportunities
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import dummy_data

# ── CSS ───────────────────────────────────────────────────────────────────────
for css_file in ("CSS_File/style.css", "CSS_File/alerts.css"):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<h1 class='page-header-title'>AI Alerts</h1>
<p class='page-header-sub'>
    Automatically detected problems and opportunities — no input needed
</p>
""", unsafe_allow_html=True)

# ── Alert Cards ───────────────────────────────────────────────────────────────
for alert in dummy_data.alerts_data:
    st.markdown(f"""
    <div class="alert-card">
        <div class="alert-card-inner">
            <div class="alert-icon" style="background:{alert['icon_bg']};">
                {alert['icon']}
            </div>
            <div style="flex:1;">
                <div class="alert-badge-row">
                    <span class="alert-title">{alert['title']}</span>
                    <span class="alert-badge"
                          style="background:{alert['badge_bg']};color:{alert['badge_color']};">
                        {alert['badge']}
                    </span>
                </div>
                <p class="alert-desc">{alert['desc']}</p>
                <div class="alert-metrics-row">
                    <div class="alert-metric-box">
                        <div class="alert-metric-label">{alert['metric_label']}</div>
                        <div class="alert-metric-value">{alert['metric_value']}</div>
                    </div>
                    <div class="alert-metric-box">
                        <div class="alert-metric-label">{alert['impact_label']}</div>
                        <div class="alert-metric-value">{alert['impact_value']}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
