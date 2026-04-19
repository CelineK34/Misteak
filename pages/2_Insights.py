import streamlit as st
import dummy_data

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

with open('alerts.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown("<h1 style='font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;'>AI Alerts</h1>",
            unsafe_allow_html=True)
st.markdown("<p style='color:#64748b;margin-top:-12px;margin-bottom:24px;'>Automatically detected problems and opportunities — no input needed</p>",
            unsafe_allow_html=True)

for alert in dummy_data.alerts_data:
    st.markdown(f"""
    <div class="alert-card">
        <div class="alert-card-inner">
            <div class="alert-icon" style="background:{alert['icon_bg']};">
                {alert['icon']}
            </div>
            <div style="flex:1;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                    <span class="alert-title">{alert['title']}</span>
                    <span class="alert-badge"
                          style="background:{alert['badge_bg']};color:{alert['badge_color']};">
                        {alert['badge']}
                    </span>
                </div>
                <p class="alert-desc">{alert['desc']}</p>
                <div style="display:flex;gap:10px;">
                    <div class="alert-metric-box">
                        <div class="alert-metric-label">METRIC</div>
                        <div class="alert-metric-value">{alert['metric_value']}</div>
                    </div>
                    <div class="alert-metric-box">
                        <div class="alert-metric-label">IMPACT</div>
                        <div class="alert-metric-value">{alert['impact_value']}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)