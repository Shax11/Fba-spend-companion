
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import load_history, load_purchases, rolling_avgs, compute_required_spend, month_start

st.set_page_config(page_title="FBA Spend Companion", page_icon="📈", layout="wide")

# ---------- Header / Hero ----------
st.markdown("""
<style>
.kpi-card{padding:16px;border-radius:16px;background:linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));border:1px solid rgba(255,255,255,0.08);}
.kpi-title{font-size:0.9rem;opacity:0.8;margin-bottom:6px}
.kpi-value{font-size:1.6rem;font-weight:700;margin:0}
.subgrid{display:grid;grid-template-columns:repeat(6,1fr);gap:14px}
@media (max-width: 900px){.subgrid{grid-template-columns:1fr 1fr}}
.section{margin-top:10px;margin-bottom:8px}
</style>
""", unsafe_allow_html=True)

st.markdown("## 📊 Amazon FBA – Spend‑to‑Profit Companion")
st.caption("A minimalist, phone‑friendly dashboard to set monthly **spend targets** that hit your **profit goal**, grounded in your historical ROI and margins.")

# ---------- Sidebar Controls ----------
with st.sidebar:
    st.header("⚙️ Settings")
    st.write("Tune your targets and model assumptions.")
    target_profit = st.number_input("Target Net Profit per Month (£)", min_value=0, value=4000, step=100)
    fixed_costs = st.number_input("Fixed Costs per Month (£)", min_value=0, value=600, step=50)
    rolling_n = st.slider("Rolling months for averages", 1, 12, 3)
    realization = st.slider("Realization (share of this month's spend that sells same month)", 0.1, 1.0, 0.7, 0.05)
    buffer = st.slider("Safety buffer on spend", 0.0, 0.5, 0.10, 0.01)
    st.divider()
    st.write("**Data files** (CSV) are in `data/`. Replace with your exports.")
    st.code("data/history.csv\ndata/purchases.csv", language="bash")

# ---------- Load Data ----------
hist = load_history()
purch = load_purchases()

avg_roi, avg_margin, avg_rev_to_spend = rolling_avgs(hist, rolling_n)
spend_roi, spend_margin, spend_blended = compute_required_spend(
    target_profit, fixed_costs, avg_roi, avg_margin, avg_rev_to_spend, realization, buffer
)

# Current month spend progress
today = month_start(pd.Timestamp.utcnow())
month_mask = (purch["Date"] >= today) & (purch["Date"] < (today + pd.offsets.MonthEnd(0) + pd.Timedelta(days=1)))
month_spend = purch.loc[month_mask & (purch["Category"]=="COGS"), "AmountGBP"].sum()

# ---------- KPI Grid ----------
st.markdown('<div class="subgrid">', unsafe_allow_html=True)

def kpi(title, value, fmt="£{:,.0f}"):
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">{title}</div><p class="kpi-value">{fmt.format(value) if value==value else "—"}</p></div>', unsafe_allow_html=True)

last_row = hist.tail(1)
kpi("Last Month Revenue", last_row["Revenue"].iloc[0] if not last_row.empty else np.nan)
kpi("Last Month Net Profit", last_row["Net_Profit"].iloc[0] if not last_row.empty else np.nan)
kpi("Avg ROI on Spend (rolling)", avg_roi, "{:.2%}")
kpi("Avg Margin on Revenue (rolling)", avg_margin, "{:.2%}")
kpi("Avg Revenue ÷ Spend (rolling)", avg_rev_to_spend, "{:,.2f}")
kpi("This Month COGS Purchases", month_spend)

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Spend Target Gauge ----------
col1, col2 = st.columns([1,1])
with col1:
    st.subheader("🎯 Spend Target (Blended)")
    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=float(month_spend),
        delta={"reference": float(spend_blended)},
        gauge={
            "axis":{"range":[0, float(max(spend_blended*1.6, 1000))]},
            "threshold":{"line":{"width":4},"thickness":0.85,"value":float(spend_blended)},
        },
        number={"prefix":"£"}
    ))
    gauge.update_layout(height=280, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(gauge, use_container_width=True)
    st.caption("Delta shows how far current month purchases are from the target spend that should achieve your profit goal, given your historical efficiency.")

with col2:
    st.subheader("📈 Required Spend (three methods)")
    tbl = pd.DataFrame({
        "Method":["ROI-on-Spend","Margin × Turn","Blended (geo mean)"],
        "Required Spend":[spend_roi, spend_margin, spend_blended]
    })
    st.dataframe(tbl.style.format({"Required Spend":"£{:,.0f}"}), use_container_width=True)

# ---------- Trends ----------
st.subheader("Trends")
c1, c2 = st.columns(2)
with c1:
    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(x=hist["Month"], y=hist["Revenue"], mode="lines+markers", name="Revenue"))
    fig_rev.update_layout(height=300, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="£")
    st.plotly_chart(fig_rev, use_container_width=True)
with c2:
    fig_np = go.Figure()
    fig_np.add_trace(go.Scatter(x=hist["Month"], y=hist["Net_Profit"], mode="lines+markers", name="Net Profit"))
    fig_np.update_layout(height=300, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="£")
    st.plotly_chart(fig_np, use_container_width=True)

# ---------- Sensitivity ----------
st.subheader("Sensitivity (What if)")
c3, c4 = st.columns(2)
with c3:
    roi_vals = np.array([0.25,0.35,0.45,0.55,0.65])
    spend_needed = (target_profit + fixed_costs) / np.maximum(roi_vals*realization, 1e-9) * (1+buffer)
    fig = go.Figure(go.Bar(x=[f"{v:.0%}" for v in roi_vals], y=spend_needed))
    fig.update_layout(height=300, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="£ spend")
    st.plotly_chart(fig, use_container_width=True)
with c4:
    real_vals = np.array([0.4,0.5,0.6,0.7,0.8])
    spend_needed2 = (target_profit + fixed_costs) / np.maximum(avg_roi*real_vals, 1e-9) * (1+buffer)
    fig2 = go.Figure(go.Bar(x=[f"{v:.0%}" for v in real_vals], y=spend_needed2))
    fig2.update_layout(height=300, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="£ spend")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.caption("Replace `data/history.csv` with SellerToolkit exports (monthly). Add your purchases to `data/purchases.csv` for live progress vs target.")
