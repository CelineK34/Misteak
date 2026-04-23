"""
pages/5_decision.py — Final AI recommendation page
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import dummy_data

for css_file in ("CSS_File/style.css", "CSS_File/decision.css"):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<h1 class='page-header-title'>Final Decision</h1>
<p class='page-header-sub'>AI's best recommended action based on your data</p>
""", unsafe_allow_html=True)

rec = dummy_data.best_recommendation

# ── Build steps separately ────────────────────────────────────
steps_html = ""
for a in rec["actions"]:
    steps_html += (
        '<div style="display:flex;align-items:center;gap:10px;padding:9px 0;'
        'border-bottom:1px solid rgba(0,0,0,0.05);">'
        '<span style="color:#008b5b;font-size:16px;font-weight:700;">&#10003;</span>'
        '<span style="font-size:14px;color:#0f172a;">' + a + '</span>'
        '</div>'
    )

# ── Build metric cards separately ────────────────────────────
metric_html = (
    '<div class="decision-metric-card">'
    '<div class="decision-metric-value" style="color:#008b5b;">' + rec['profit_impact'] + '</div>'
    '<div class="decision-metric-label">Profit Impact</div>'
    '</div>'
    '<div class="decision-metric-card">'
    '<div class="decision-metric-value" style="color:' + rec['risk_color'] + ';">' + rec['risk'] + '</div>'
    '<div class="decision-metric-label">Risk Level</div>'
    '</div>'
    '<div class="decision-metric-card">'
    '<div class="decision-metric-value">' + str(rec['confidence']) + '%</div>'
    '<div class="decision-metric-label">AI Confidence</div>'
    '</div>'
)

# ── Hero card ─────────────────────────────────────────────────
hero_html = (
    '<div class="decision-hero">'
    '<div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;">'
    '<div style="background:#d0f5e8;border-radius:12px;width:50px;height:50px;'
    'display:flex;align-items:center;justify-content:center;font-size:24px;">🏆</div>'
    '<div>'
    '<div class="decision-rec-label">Recommended Strategy</div>'
    '<div class="decision-title">' + rec['title'] + '</div>'
    '</div>'
    '</div>'
    '<p class="decision-desc">' + rec['desc'] + '</p>'
    '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;">'
    + metric_html +
    '</div>'
    '<div style="font-size:10px;font-weight:600;color:#94a3b8;'
    'letter-spacing:0.08em;text-transform:uppercase;margin-bottom:10px;">'
    'Implementation Steps</div>'
    + steps_html +
    '<div class="decision-why">'
    '<div class="decision-why-label">Why this strategy?</div>'
    '<div class="decision-why-text">' + rec['why'] + '</div>'
    '</div>'
    '</div>'
)

st.markdown(hero_html, unsafe_allow_html=True)

# ── Expected Results ──────────────────────────────────────────
e1, e2, e3, e4 = st.columns(4)

for col, label, value in zip(
    [e1, e2, e3, e4],
    ["Expected Revenue", "Expected Profit", "Expected Orders", "Timeline"],
    [rec["expected_revenue"], rec["expected_profit"], rec["expected_orders"], rec["timeline"]],
):
    with col:
        st.markdown(
            '<div class="decision-expected-card">'
            '<div class="decision-expected-val">' + value + '</div>'
            '<div class="decision-expected-lbl">' + label + '</div>'
            '</div>',
            unsafe_allow_html=True
        )

# ── Other Options ─────────────────────────────────────────────
other_rows_html = ""
for opt in rec["other_options"]:
    other_rows_html += (
        '<div class="other-option-row">'
        '<div>'
        '<div class="other-option-name">' + opt['title'] + '</div>'
        '<div class="other-option-meta">' + opt['risk'] + ' risk &middot; ' + str(opt['confidence']) + '% confidence</div>'
        '</div>'
        '<div class="other-option-profit">' + opt['profit_impact'] + '</div>'
        '</div>'
    )

st.markdown(
    '<div class="other-options-card">'
    '<div class="other-options-label">Other Options Considered</div>'
    + other_rows_html +
    '</div>',
    unsafe_allow_html=True
)

# ── Back Button ───────────────────────────────────────────────
st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
if st.button("← Back to Strategies"):
    st.switch_page("pages/3_strategies.py")