import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
import sys

sys.path.append(os.path.abspath('.'))
from src.portfolio_limits_monitor import PortfolioLimitsMonitor
from src.credit_triggers_backtest import CreditTriggersBacktester

st.set_page_config(page_title="Credit Risk LOD2 Dashboard", layout="wide", page_icon="🏦")
DB_PATH = 'data/risk_portfolio.db'

@st.cache_data
def load_latest_portfolio():
    return PortfolioLimitsMonitor(db_path=DB_PATH).get_latest_exposures()

@st.cache_data
def load_breaches():
    monitor = PortfolioLimitsMonitor(db_path=DB_PATH)
    return monitor.get_lll_breaches(), monitor.get_large_exposures()

@st.cache_data
def run_and_load_backtester():
    return CreditTriggersBacktester(db_path=DB_PATH).run_backtest()

st.title("🏦 Credit Portfolio Governance Engine - LOD2")
st.markdown("Quantitative Risk Monitoring for Corporate & Institutional Banking")

df = load_latest_portfolio()
lll_breaches, large_exp = load_breaches()
alerts = run_and_load_backtester()

st.sidebar.header("Risk Filters")
selected_sector = st.sidebar.multiselect("Sector", df['Sector'].unique(), default=df['Sector'].unique())
selected_region = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
filtered_df = df[(df['Sector'].isin(selected_sector)) & (df['Region'].isin(selected_region))]

filtered_df['Total_Exposure'] = filtered_df['Drawn_Amount'] + filtered_df['Trading_MtM'].clip(lower=0) + filtered_df['PFE']
total_exp = filtered_df['Total_Exposure'].sum()
total_breach_amt = lll_breaches['Breach_Amount'].sum()
watchlist_cnt = len(filtered_df[filtered_df['Internal_Rating'].isin(['CCC', 'D'])])
avg_utilization = (filtered_df['Drawn_Amount'].sum() / filtered_df['Approved_Limit'].sum()) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Net Exposure", f"${total_exp / 1e9:.2f} B")
col2.metric("Total LLL Breaches", f"${total_breach_amt / 1e6:.2f} M", delta=f"{len(lll_breaches)} facilities", delta_color="inverse")
col3.metric("CCC/D Watchlist Count", watchlist_cnt)
col4.metric("Avg Facility Utilization", f"{avg_utilization:.1f} %")
st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Portfolio Overview", "🚨 Limits & Regulatory", "⏱️ Backtesting"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_tree = px.treemap(filtered_df, path=[px.Constant("Portfolio"), 'Region', 'Sector'], values='Total_Exposure', title="Exposure Treemap", template="plotly_dark")
        st.plotly_chart(fig_tree, use_container_width=True)
    with c2:
        rating_exp = filtered_df.groupby('Internal_Rating')['Total_Exposure'].sum().reset_index()
        rating_order = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'D']
        rating_exp['Internal_Rating'] = pd.Categorical(rating_exp['Internal_Rating'], categories=rating_order, ordered=True)
        rating_exp = rating_exp.sort_values('Internal_Rating')
        fig_bar = px.bar(rating_exp, x='Internal_Rating', y='Total_Exposure', color='Internal_Rating', title="Exposure by Rating", template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**Large Exposures (>10% Tier 1 Capital)**")
        st.dataframe(large_exp[['Name', 'Sector', 'Pct_Tier1']])
    with c2:
        st.markdown("**Legal Lending Limit (LLL) Breaches**")
        st.dataframe(lll_breaches[['Facility_ID', 'Name', 'Total_Exposure', 'Breach_Amount']])

with tab3:
    if alerts.empty:
        st.success("No triggers detected.")
    else:
        fig_timeline = px.scatter(alerts, x='Reporting_Date', y='Utilization', color='New_Rating', size='PFE', title="Triggers Timeline vs Utilization", template="plotly_dark")
        st.plotly_chart(fig_timeline, use_container_width=True)
        st.dataframe(alerts[['Month', 'Obligor_ID', 'Old_Rating', 'New_Rating', 'Utilization', 'Alert_Type']])
