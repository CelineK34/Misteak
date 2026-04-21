import streamlit as st
import plotly.graph_objects as go
import dummy_data

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
with open('simulator.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stTickBarMin"],
[data-testid="stTickBarMax"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}
[data-baseweb="tooltip"],
[data-baseweb="popover"] {
    display: none !important;
    visibility: hidden !important;
}
[data-testid="stSlider"] [role="slider"] {
    background-color: #008b5b !important;
    border-color: #008b5b !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child > div:nth-child(1) {
    background: #008b5b !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child > div:nth-child(2) {
    background: #008b5b !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child > div:nth-child(3) {
    background: #e2e8f0 !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child > div:nth-child(4) {
    background: #e2e8f0 !important;
}
[data-testid="stSlider"] div[data-baseweb="slider"] div[role="progressbar"] {
    background-color: #008b5b !important;
}
[data-testid="stSlider"] div[data-baseweb="slider"] > div > div[style] {
    background-color: #008b5b !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border-color: #008b5b !important;
    border-radius: 8px !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    border: 0.5px solid #e2e8f0 !important;
    background: white !important;
    padding: 8px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;'>Scenario Simulator</h1>",
            unsafe_allow_html=True)
st.markdown('<p style="color:#64748b;margin-top:-12px;margin-bottom:24px;">"What if...?" — Predict profit & demand impact before making changes</p>',
            unsafe_allow_html=True)

items = dummy_data.simulator_items
col1, col2 = st.columns([1, 1.5])

price_range = list(range(-30, 31))
cost_range  = list(range(-30, 31))

with col1:
    with st.container(border=True):
        st.markdown("<div style='font-weight:700;font-size:16px;color:#0f172a;margin-bottom:8px;'>Adjust Parameters</div>",
                    unsafe_allow_html=True)
        st.markdown("<div style='font-size:14px;font-weight:500;color:#0f172a;margin-bottom:4px;'>Select Item</div>",
                    unsafe_allow_html=True)

        selected = st.selectbox("", list(items.keys()), label_visibility="collapsed")
        item = items[selected]

        st.markdown("<p style='font-size:14px;font-weight:500;color:#0f172a;margin-bottom:0;'>Price Change</p>",
                    unsafe_allow_html=True)
        price_pct = st.select_slider(
            "Price Change",
            options=price_range,
            value=0,
            key="price",
            label_visibility="collapsed",
            format_func=lambda x: f"{x:+d}%" if x in [-30, 0, 30] else ""
        )
        st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

        st.markdown("<p style='font-size:14px;font-weight:500;color:#0f172a;margin-bottom:0;'>Cost Change</p>",
                    unsafe_allow_html=True)
        cost_pct = st.select_slider(
            "Cost Change",
            options=cost_range,
            value=0,
            key="cost",
            label_visibility="collapsed",
            format_func=lambda x: f"{x:+d}%" if x in [-30, 0, 30] else ""
        )
        st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

        # ── Calculations ─────────────────────────────────────
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

with col2:
    with st.container(border=True):
        st.markdown(f"""
        <div style="font-weight:700;font-size:16px;color:#0f172a;margin-bottom:4px;">
            Current vs Simulated ({selected})</div>
        """, unsafe_allow_html=True)

        fig = go.Figure()
        categories     = ["Revenue", "Cost", "Profit"]
        current_vals   = [curr_revenue, curr_cost_t, curr_profit]
        simulated_vals = [sim_revenue,  sim_cost_t,  sim_profit]

        fig.add_trace(go.Bar(
            name="Current (RM)",
            x=categories, y=current_vals,
            marker_color="#94a3b8", width=0.3,
        ))
        fig.add_trace(go.Bar(
            name="Simulated (RM)",
            x=categories, y=simulated_vals,
            marker_color="#008b5b", width=0.3,
        ))
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color="#1e293b", size=12),
            barmode="group", bargroupgap=0.2,
            xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0"),
            yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", showgrid=True),
            legend=dict(orientation="h", yanchor="top", y=-0.15,
                        xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=10, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)