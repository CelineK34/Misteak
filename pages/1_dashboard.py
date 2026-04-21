"""
pages/1_dashboard.py — Dashboard overview page
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import dummy_data

# ── CSS ───────────────────────────────────────────────────────────────────────
for css_file in ("CSS_File/style.css", "CSS_File/dashboard.css"):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<h1 class='page-header-title'>Dashboard</h1>
<p class='page-header-sub'>Your F&amp;B business performance at a glance</p>
""", unsafe_allow_html=True)

# ── Alert Banner ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="alert-box">
    <span class="alert-text">
        ⚠️ <strong>2 critical AI alerts</strong> need your attention today
    </span>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
data = dummy_data.kpi_data

def render_kpi_card(title, value, trend, is_positive):
    icon  = "↑" if is_positive else "↓"
    cls   = "trend-up" if is_positive else "trend-down"
    sign  = "+" if is_positive else ""
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <span class="trend-badge {cls}">{icon} {sign}{trend}% vs last week</span>
    </div>"""

cards_html = "".join(
    render_kpi_card(k, v["value"], v["trend"], v["is_positive"])
    for k, v in data.items()
)
st.markdown(f'<div class="kpi-card-container">{cards_html}</div>', unsafe_allow_html=True)

# ── Charts Row ────────────────────────────────────────────────────────────────
df = dummy_data.trend_df
col_trend, col_bar = st.columns([1.7, 1])

with col_trend:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Revenue"], name="Revenue (RM)",
        mode="lines",
        line=dict(color="#008b5b", width=2.5, shape="spline", smoothing=1.3),
        fill="tozeroy", fillcolor="rgba(0,139,91,0.08)",
    ))
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Profit"], name="Profit (RM)",
        mode="lines",
        line=dict(color="#5ecfa0", width=2, shape="spline", smoothing=1.3),
        fill="tozeroy", fillcolor="rgba(94,207,160,0.08)",
    ))
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(color="#1e293b", size=12),
        xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", tickformat="%b %d"),
        yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="x unified",
    )
    st.markdown("""
    <div class="chart-header">
        <div class="chart-header-title">Revenue &amp; Profit Trend</div>
        <div class="chart-header-sub">Weekly rolling — last 17 weeks</div>
    </div>""", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

with col_bar:
    fig2 = px.bar(
        dummy_data.item_profit_df, x="Profit", y="Item",
        orientation="h", color_discrete_sequence=["#008b5b"],
    )
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(color="#1e293b", size=12),
        showlegend=False,
        xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0",
                   title="Profit (RM)", tickprefix="RM "),
        yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", title=""),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.markdown("""
    <div class="chart-header">
        <div class="chart-header-title">Profit by Item</div>
        <div class="chart-header-sub">This month</div>
    </div>""", unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)

# ── Performer Cards ───────────────────────────────────────────────────────────
def render_performer_row(rank, name, margin, revenue, is_top):
    rank_cls    = "rank-top" if is_top else "rank-attn"
    revenue_cls = "revenue-top" if is_top else "revenue-attn"
    return f"""
    <div class="performer-row">
        <div class="performer-inner">
            <div class="performer-rank {rank_cls}">{rank}</div>
            <div>
                <div class="performer-name">{name}</div>
                <div class="performer-meta">{margin}</div>
            </div>
        </div>
        <div class="performer-revenue {revenue_cls}">{revenue}</div>
    </div>"""

col_top, col_attn = st.columns(2)

with col_top:
    rows = "".join(
        render_performer_row(i + 1, r["Item"], r["Margin"], r["Revenue"], True)
        for i, r in dummy_data.top_performers_df.iterrows()
    )
    st.markdown(f"""
    <div class="performer-card">
        <div class="performer-card-title">⚡ Top Performers</div>
        {rows}
    </div>""", unsafe_allow_html=True)

with col_attn:
    rows = "".join(
        render_performer_row(i + 1, r["Item"], r["Margin"], r["Revenue"], False)
        for i, r in dummy_data.needs_attention_df.iterrows()
    )
    st.markdown(f"""
    <div class="performer-card">
        <div class="performer-card-title">⚠️ Needs Attention</div>
        {rows}
    </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-footer">AI-Powered · FoodAI · Decisions based on your real sales data</div>',
    unsafe_allow_html=True,
)
