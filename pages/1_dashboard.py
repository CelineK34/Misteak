import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import dummy_data

with open('dashboard.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown("<h1 style='font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px;'>Dashboard</h1>",
            unsafe_allow_html=True)
st.markdown("<p style='color:#64748b;margin-top:-12px'>Your F&B business performance at a glance</p>",
            unsafe_allow_html=True)

st.markdown("""
<div class="alert-box">
    <span class="alert-text">⚠️ 2 AI alerts need your attention</span>
</div>""", unsafe_allow_html=True)

# ── KPI Cards ────────────────────────────────────────────────
data = dummy_data.kpi_data

def render_card(title, value, trend, is_positive):
    icon = "↑" if is_positive else "↓"
    cls  = "trend-up" if is_positive else "trend-down"
    sign = "+" if is_positive else ""
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div><span class="trend-badge {cls}">{icon} {sign}{trend}% vs last week</span></div>
    </div>"""

cards = (
    render_card("Total Revenue", data["Total Revenue"]["value"], data["Total Revenue"]["trend"], data["Total Revenue"]["is_positive"]) +
    render_card("Total Profit",  data["Total Profit"]["value"],  data["Total Profit"]["trend"],  data["Total Profit"]["is_positive"]) +
    render_card("Total Orders",  data["Total Orders"]["value"],  data["Total Orders"]["trend"],  data["Total Orders"]["is_positive"]) +
    render_card("Avg Margin",    data["Avg Margin"]["value"],    data["Avg Margin"]["trend"],    data["Avg Margin"]["is_positive"])
)
st.markdown(f'<div class="kpi-card-container">{cards}</div>', unsafe_allow_html=True)

# ── Charts ───────────────────────────────────────────────────
df = dummy_data.trend_df
c1, c2 = st.columns([2, 1])

with c1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Revenue"], name="Revenue",
        mode="lines",
        line=dict(color="#008b5b", width=2.5, shape="spline", smoothing=1.3),
        fill="tozeroy", fillcolor="rgba(0,139,91,0.10)"
    ))
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Profit"], name="Profit",
        mode="lines",
        line=dict(color="#5ecfa0", width=2, shape="spline", smoothing=1.3),
        fill="tozeroy", fillcolor="rgba(94,207,160,0.10)"
    ))
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(color="#1e293b", size=12),
        xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", showgrid=True,
                   tickformat="%b %d\n%Y"),
        yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", showgrid=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="x unified"
    )
    st.markdown("""
    <div style="background:white;border-radius:16px 16px 0 0;padding:20px 20px 0 20px;
                border:0.5px solid #e2e8f0;border-bottom:none;">
        <div style="font-weight:700;font-size:16px;color:#0f172a;">
            Revenue &amp; Profit Trend</div>
    </div>""", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig2 = px.bar(
        dummy_data.item_profit_df, x="Profit", y="Item",
        orientation='h', color_discrete_sequence=["#008b5b"],
    )
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(color="#1e293b", size=12),
        showlegend=False,
        xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", title="Profit"),
        yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0", title=""),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.markdown("""
    <div style="background:white;border-radius:16px 16px 0 0;padding:20px 20px 0 20px;
                border:0.5px solid #e2e8f0;border-bottom:none;">
        <div style="font-weight:700;font-size:16px;color:#0f172a;">
            Profit by Item</div>
    </div>""", unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)

# ── Performer Cards ───────────────────────────────────────────
def render_row(rank, name, margin, revenue, is_top):
    badge_bg  = "#d0f5e8" if is_top else ["#fee2e2","#fef3c7","#fef3c7"][min(rank-1,2)]
    badge_txt = "#005c3e" if is_top else ["#991b1b","#92400e","#92400e"][min(rank-1,2)]
    val_color = "#008b5b" if is_top else "#64748b"
    return f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                background:#f8fafc;border-radius:10px;padding:14px 16px;margin-bottom:10px;">
        <div style="display:flex;align-items:center;gap:14px;">
            <div style="width:28px;height:28px;border-radius:50%;background:{badge_bg};
                        color:{badge_txt};display:flex;align-items:center;justify-content:center;
                        font-size:13px;font-weight:600;">{rank}</div>
            <div>
                <div style="font-weight:600;color:#0f172a;font-size:14px;">{name}</div>
                <div style="color:#64748b;font-size:12px;">{margin} margin</div>
            </div>
        </div>
        <div style="font-weight:700;color:{val_color};font-size:15px;">{revenue}</div>
    </div>"""

p1, p2 = st.columns(2)

with p1:
    rows = "".join(
        render_row(i+1, r["Item"], r["Margin"], r["Revenue"], True)
        for i, r in dummy_data.top_performers_df.iterrows()
    )
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:20px;
                border:0.5px solid #e2e8f0;margin-top:16px;">
        <div style="font-weight:700;font-size:16px;color:#0f172a;margin-bottom:14px;">
            ⚡ Top Performers</div>
        {rows}
    </div>""", unsafe_allow_html=True)

with p2:
    rows = "".join(
        render_row(i+1, r["Item"], r["Margin"], r["Revenue"], False)
        for i, r in dummy_data.needs_attention_df.iterrows()
    )
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:20px;
                border:0.5px solid #e2e8f0;margin-top:16px;">
        <div style="font-weight:700;font-size:16px;color:#0f172a;margin-bottom:14px;">
            ⚠️ Needs Attention</div>
        {rows}
    </div>""", unsafe_allow_html=True)

st.markdown("""
<div class="dashboard-footer">AI-Powered · Decisions based on your real sales data</div>
""", unsafe_allow_html=True)