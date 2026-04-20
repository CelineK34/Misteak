import streamlit as st
import plotly.graph_objects as go
import dummy_data

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
with open('simulator.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Style sliders green
st.markdown("""
<style>
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background-color: #008b5b !important;
    border-color: #008b5b !important;
}
[data-testid="stSlider"] div[data-baseweb="slider"] > div:nth-child(2) > div {
    background: #008b5b !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border-color: #008b5b !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;'>Scenario Simulator</h1>",
            unsafe_allow_html=True)
st.markdown('<p style="color:#64748b;margin-top:-12px;margin-bottom:24px;">"What if...?" — Predict profit & demand impact before making changes</p>',
            unsafe_allow_html=True)

items = dummy_data.simulator_items
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown('<div class="sim-card">', unsafe_allow_html=True)
    st.markdown('<div class="sim-card-title">Adjust Parameters</div>', unsafe_allow_html=True)

    # Item selector
    st.markdown('<p style="font-size:14px;font-weight:500;color:#0f172a;margin-bottom:6px;">Select Item</p>',
                unsafe_allow_html=True)
    selected = st.selectbox("", list(items.keys()), label_visibility="collapsed")
    item = items[selected]

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Price slider
    price_pct = st.slider("Price Change", -30, 30, 0, key="price")
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;font-size:11px;
                color:#94a3b8;margin-top:-12px;margin-bottom:8px;">
        <span>-30%</span><span>0</span><span>+30%</span>
    </div>""", unsafe_allow_html=True)

    # Cost slider
    cost_pct = st.slider("Cost Change", -30, 30, 0, key="cost")
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;font-size:11px;
                color:#94a3b8;margin-top:-12px;margin-bottom:16px;">
        <span>-30%</span><span>0</span><span>+30%</span>
    </div>""", unsafe_allow_html=True)

    # ── Calculations ──────────────────────────────────────────
    new_price    = item["price"] * (1 + price_pct / 100)
    new_cost     = item["cost"]  * (1 + cost_pct  / 100)
    demand_chg   = item["elasticity"] * price_pct
    new_qty      = max(0, item["qty"] * (1 + demand_chg / 100))
    curr_revenue = item["price"] * item["qty"]
    curr_cost_t  = item["cost"]  * item["qty"]
    curr_profit  = curr_revenue  - curr_cost_t
    sim_revenue  = new_price * new_qty
    sim_cost_t   = new_cost  * new_qty
    sim_profit   = sim_revenue - sim_cost_t
    profit_chg   = ((sim_profit - curr_profit) / curr_profit * 100) if curr_profit != 0 else 0

    demand_str = f"+{demand_chg:.1f}%" if demand_chg >= 0 else f"{demand_chg:.1f}%"
    profit_str = f"+{profit_chg:.1f}%" if profit_chg >= 0 else f"{profit_chg:.1f}%"
    demand_cls = "impact-positive" if demand_chg >= 0 else "impact-negative"
    profit_cls = "impact-positive" if profit_chg >= 0 else "impact-negative"
    price_display = f"+{price_pct}%" if price_pct >= 0 else f"{price_pct}%"
    cost_display  = f"+{cost_pct}%"  if cost_pct  >= 0 else f"{cost_pct}%"

    st.markdown(f"""
    <div class="predicted-impact">
        <div class="predicted-impact-title">PREDICTED IMPACT</div>
        <div class="impact-row">
            <span>Demand</span>
            <span class="{demand_cls}">{demand_str}</span>
        </div>
        <div class="impact-row">
            <span>Profit</span>
            <span class="{profit_cls}">{profit_str}</span>
        </div>
        <div class="impact-row">
            <span>New Qty</span>
            <span class="impact-neutral">{int(new_qty)} units</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:24px;border:0.5px solid #e2e8f0;">
        <div style="font-weight:700;font-size:16px;color:#0f172a;margin-bottom:16px;">
            Current vs Simulated ({selected})</div>
    </div>""", unsafe_allow_html=True)

    fig = go.Figure()

    categories = ["Revenue", "Cost", "Profit"]
    current_vals  = [curr_revenue, curr_cost_t, curr_profit]
    simulated_vals = [sim_revenue,  sim_cost_t,  sim_profit]

    fig.add_trace(go.Bar(
        name="Current (RM)",
        x=categories,
        y=current_vals,
        marker_color="#94a3b8",
        width=0.3,
    ))
    fig.add_trace(go.Bar(
        name="Simulated (RM)",
        x=categories,
        y=simulated_vals,
        marker_color="#008b5b",
        width=0.3,
    ))

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#1e293b", size=12),
        barmode="group",
        bargroupgap=0.2,
        xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0"),
        yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", showgrid=True),
        legend=dict(orientation="h", yanchor="top", y=-0.15,
                    xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=10, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)