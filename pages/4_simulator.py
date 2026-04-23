"""
pages/4_simulator.py — "What if?" scenario simulator
"""
import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import dummy_data

# ── CSS ───────────────────────────────────────────────────────────────────────
for css_file in ("CSS_File/style.css", "CSS_File/simulator.css"):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<h1 class='page-header-title'>Scenario Simulator</h1>
<p class='page-header-sub'>"What if…?" — Predict profit &amp; demand impact before making changes</p>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
items = dummy_data.simulator_items
col_controls, col_chart = st.columns([1, 1.5])

with col_controls:
    with st.container(border=True):
        st.markdown(
            "<div style='font-weight:700;font-size:15px;color:#0f172a;margin-bottom:12px;'>"
            "Adjust Parameters</div>",
            unsafe_allow_html=True,
        )

        # Item selector
        st.markdown(
            "<div style='font-size:13px;font-weight:500;color:#0f172a;margin-bottom:4px;'>"
            "Select Item</div>",
            unsafe_allow_html=True,
        )
        selected = st.selectbox("", list(items.keys()), label_visibility="collapsed")
        item = items[selected]

        # Price slider
        st.markdown(
            "<p style='font-size:13px;font-weight:500;color:#0f172a;margin-bottom:0;'>"
            "Price Change</p>",
            unsafe_allow_html=True,
        )
        price_pct = st.select_slider(
            "Price Change",
            options=list(range(-30, 31)),
            value=0,
            key="price_slider",
            label_visibility="collapsed",
            format_func=lambda x: f"{x:+d}%" if x in (-30, 0, 30) else "",
        )
        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

        # Cost slider
        st.markdown(
            "<p style='font-size:13px;font-weight:500;color:#0f172a;margin-bottom:0;'>"
            "Cost Change</p>",
            unsafe_allow_html=True,
        )
        cost_pct = st.select_slider(
            "Cost Change",
            options=list(range(-30, 31)),
            value=0,
            key="cost_slider",
            label_visibility="collapsed",
            format_func=lambda x: f"{x:+d}%" if x in (-30, 0, 30) else "",
        )
        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

        # ── Calculations ─────────────────────────────────────────────────────
        new_price    = item["price"] * (1 + price_pct / 100)
        new_cost     = item["cost"]  * (1 + cost_pct  / 100)
        demand_chg   = item["elasticity"] * price_pct
        new_qty      = max(0.0, item["qty"] * (1 + demand_chg / 100))
        curr_revenue = item["price"] * item["qty"]
        curr_cost_t  = item["cost"]  * item["qty"]
        curr_profit  = curr_revenue  - curr_cost_t
        sim_revenue  = new_price * new_qty
        sim_cost_t   = new_cost  * new_qty
        sim_profit   = sim_revenue - sim_cost_t
        profit_chg   = ((sim_profit - curr_profit) / curr_profit * 100) if curr_profit else 0

        def fmt(val: float, suffix: str = "%") -> tuple[str, str]:
            """Return (formatted string, CSS class)."""
            sign = "+" if val >= 0 else ""
            cls  = "impact-positive" if val > 0 else ("impact-negative" if val < 0 else "impact-neutral")
            return f"{sign}{val:.1f}{suffix}", cls

        demand_str, demand_cls = fmt(demand_chg)
        profit_str, profit_cls = fmt(profit_chg)
        rev_str,    rev_cls    = fmt(sim_revenue - curr_revenue, " RM")

        st.markdown(f"""
        <div class="predicted-impact">
            <div class="predicted-impact-title">Predicted Impact</div>
            <div class="impact-row">
                <span>Demand change</span>
                <span class="{demand_cls}">{demand_str}</span>
            </div>
            <div class="impact-row">
                <span>Profit change</span>
                <span class="{profit_cls}">{profit_str}</span>
            </div>
            <div class="impact-row">
                <span>New daily qty</span>
                <span class="impact-neutral">{int(new_qty)} units</span>
            </div>
            <div class="impact-row">
                <span>New daily revenue</span>
                <span class="{rev_cls}">RM {sim_revenue:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Chart ─────────────────────────────────────────────────────────────────────
with col_chart:
    with st.container(border=True):
        st.markdown(
            f"<div style='font-weight:700;font-size:15px;color:#0f172a;margin-bottom:8px;'>"
            f"Current vs Simulated — {selected}</div>",
            unsafe_allow_html=True,
        )

        categories     = ["Revenue", "Cost", "Profit"]
        current_vals   = [curr_revenue, curr_cost_t,  curr_profit]
        simulated_vals = [sim_revenue,  sim_cost_t,   sim_profit]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Current (RM)",
            x=categories, y=current_vals,
            marker_color="#cbd5e1", width=0.3,
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
            yaxis=dict(
                gridcolor="#f1f5f9", linecolor="#e2e8f0",
                tickprefix="RM ", showgrid=True,
            ),
            legend=dict(
                orientation="h", yanchor="top", y=-0.12,
                xanchor="center", x=0.5,
                bgcolor="rgba(0,0,0,0)",
            ),
            margin=dict(l=10, r=10, t=10, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
