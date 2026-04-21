import streamlit as st
import dummy_data

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
with open('decision.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

rec = dummy_data.best_recommendation

st.markdown("<h1 style='font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;'>Final Decision</h1>",
            unsafe_allow_html=True)
st.markdown("<p style='color:#64748b;margin-top:-12px;margin-bottom:24px;'>AI's best recommended action</p>",
            unsafe_allow_html=True)

steps_html = "".join(
    f"""<div style="display:flex;align-items:center;gap:10px;padding:8px 0;
                    border-bottom:0.5px solid #f1f5f9;">
            <span style="color:#008b5b;font-size:18px;">&#10003;</span>
            <span style="font-size:14px;color:#0f172a;">{a}</span>
        </div>"""
    for a in rec["actions"]
)

st.markdown(f"""
<div style="background:#f0fdf8;border-radius:16px;padding:28px;
            border:0.5px solid #d0f5e8;margin-bottom:20px;">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
        <div style="background:#d0f5e8;border-radius:12px;width:48px;height:48px;
                    display:flex;align-items:center;justify-content:center;font-size:22px;">
            🏆
        </div>
        <div>
            <div style="font-size:11px;font-weight:600;color:#008b5b;
                        letter-spacing:0.08em;margin-bottom:2px;">RECOMMENDED STRATEGY</div>
            <div style="font-size:22px;font-weight:700;color:#0f172a;">{rec['title']}</div>
        </div>
    </div>
    <p style="font-size:14px;color:#64748b;margin:8px 0 20px 0;line-height:1.6;">{rec['desc']}</p>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;">
        <div style="background:white;border-radius:12px;padding:20px;
                    border:0.5px solid #e2e8f0;text-align:center;">
            <div style="color:#008b5b;font-size:18px;margin-bottom:4px;">&#8599;</div>
            <div style="font-size:26px;font-weight:700;color:#008b5b;">{rec['profit_impact']}</div>
            <div style="font-size:11px;font-weight:600;color:#94a3b8;
                        letter-spacing:0.06em;margin-top:4px;">PROFIT IMPACT</div>
        </div>
        <div style="background:white;border-radius:12px;padding:20px;
                    border:0.5px solid #e2e8f0;text-align:center;">
            <div style="color:{rec['risk_color']};font-size:18px;margin-bottom:4px;">&#9711;</div>
            <div style="font-size:26px;font-weight:700;color:{rec['risk_color']};">{rec['risk']}</div>
            <div style="font-size:11px;font-weight:600;color:#94a3b8;
                        letter-spacing:0.06em;margin-top:4px;">RISK LEVEL</div>
        </div>
        <div style="background:white;border-radius:12px;padding:20px;
                    border:0.5px solid #e2e8f0;text-align:center;">
            <div style="font-size:13px;font-weight:700;color:#64748b;margin-bottom:4px;">AI</div>
            <div style="font-size:26px;font-weight:700;color:#0f172a;">{rec['confidence']}%</div>
            <div style="font-size:11px;font-weight:600;color:#94a3b8;
                        letter-spacing:0.06em;margin-top:4px;">CONFIDENCE</div>
        </div>
    </div>
    <div style="font-size:11px;font-weight:600;color:#94a3b8;
                letter-spacing:0.08em;margin-bottom:10px;">IMPLEMENTATION STEPS</div>
    {steps_html}
    <div style="background:#d0f5e8;border-radius:10px;padding:16px 18px;margin-top:20px;">
        <div style="font-size:11px;font-weight:600;color:#008b5b;
                    letter-spacing:0.08em;margin-bottom:6px;">WHY THIS STRATEGY?</div>
        <div style="font-size:13px;color:#374151;line-height:1.6;">{rec['why']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Expected Results ──────────────────────────────────────────
e1, e2, e3, e4 = st.columns(4)

with e1:
    st.markdown(f"""
    <div class="decision-metric-card">
        <div class="decision-metric-label">EXPECTED REVENUE</div>
        <div class="decision-metric-value" style="font-size:20px;">{rec['expected_revenue']}</div>
    </div>""", unsafe_allow_html=True)

with e2:
    st.markdown(f"""
    <div class="decision-metric-card">
        <div class="decision-metric-label">EXPECTED PROFIT</div>
        <div class="decision-metric-value" style="font-size:20px;">{rec['expected_profit']}</div>
    </div>""", unsafe_allow_html=True)

with e3:
    st.markdown(f"""
    <div class="decision-metric-card">
        <div class="decision-metric-label">EXPECTED ORDERS</div>
        <div class="decision-metric-value" style="font-size:20px;">{rec['expected_orders']}</div>
    </div>""", unsafe_allow_html=True)

with e4:
    st.markdown(f"""
    <div class="decision-metric-card">
        <div class="decision-metric-label">TIMELINE</div>
        <div class="decision-metric-value" style="font-size:20px;">{rec['timeline']}</div>
    </div>""", unsafe_allow_html=True)

# ── Other Options ─────────────────────────────────────────────
other_rows = ""
for opt in rec["other_options"]:
    other_rows += (
        '<div style="display:flex;justify-content:space-between;align-items:center;'
        'padding:12px 0;border-bottom:0.5px solid #f1f5f9;">'
        '<div>'
        '<div style="font-size:14px;font-weight:600;color:#0f172a;margin-bottom:2px;">'
        + opt['title'] +
        '</div>'
        '<div style="font-size:12px;color:#94a3b8;">'
        + opt['risk'] + ' risk &middot; ' + str(opt['confidence']) + '% confidence'
        '</div>'
        '</div>'
        '<div style="font-size:14px;font-weight:700;color:#008b5b;white-space:nowrap;padding-left:16px;">'
        + opt['profit_impact'] +
        '</div>'
        '</div>'
    )

st.markdown(
    '<div style="background:white;border-radius:14px;padding:24px;'
    'border:0.5px solid #e2e8f0;margin-top:16px;">'
    '<div style="font-size:11px;font-weight:600;color:#94a3b8;'
    'letter-spacing:0.08em;margin-bottom:4px;">OTHER OPTIONS CONSIDERED</div>'
    + other_rows +
    '</div>',
    unsafe_allow_html=True
)

# ── Back button ───────────────────────────────────────────────
st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
if st.button("← Back to Strategies"):
    st.switch_page("pages/3_Strategy.py")

st.markdown("""
<style>
[data-testid="stButton"] button {
    background-color: #008b5b !important;
    border-color: #008b5b !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 8px 20px !important;
    font-size: 14px !important;
}
[data-testid="stButton"] button:hover {
    background-color: #006e48 !important;
    border-color: #006e48 !important;
}
</style>
""", unsafe_allow_html=True)