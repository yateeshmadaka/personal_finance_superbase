import streamlit as st
import db_manager as db
import pandas as pd
from datetime import date
import plotly.express as px

st.set_page_config(
    page_title="Personal Finance",
    page_icon="💰",
    layout="wide"
)

# Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #00FF00;
    }
    .metric-label {
        color: #888;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

def format_currency(amount):
    return f"₹{amount:,.0f}".replace(",", ",") # No need to replace comma with space for INR usually, but following style if needed or just standard comma
    # Actually user asked for XPF space format "12 345 XPF", for INR standard is often "₹ 12,345". 
    # Let's use "₹ 12,345"
    return f"₹ {amount:,.0f}"

st.title("💸 Personal Finance Dashboard")

# Sidebar - Month Selection
st.sidebar.header("Dashboard Filters")
today = date.today()
selected_year = st.sidebar.number_input("Year", min_value=2000, max_value=2100, value=today.year)
selected_month = st.sidebar.selectbox("Month", range(1, 13), index=today.month - 1)

# Fetch Data
total_rev, total_exp, budget_amt = db.get_monthly_summary(selected_year, selected_month)
net_savings = total_rev - total_exp
remaining_budget = budget_amt - total_exp

# KPI Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Revenue", format_currency(total_rev))

with col2:
    st.metric("Total Expenses", format_currency(total_exp), delta=f"{-(total_exp/budget_amt)*100:.1f}% of Budget" if budget_amt > 0 else None, delta_color="inverse")

with col3:
    st.metric("Net Savings", format_currency(net_savings), delta_color="normal" if net_savings >= 0 else "inverse")

with col4:
    st.metric("Remaining Budget", format_currency(remaining_budget), delta_color="normal" if remaining_budget >= 0 else "inverse")


st.divider()

# Charts
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(f"Expense Breakdown ({selected_month}/{selected_year})")
    expense_df = db.get_expense_breakdown(selected_year, selected_month)
    if not expense_df.empty:
        fig_pie = px.pie(expense_df, values='total', names='type', hole=0.4, color_discrete_sequence=px.colors.sequential.Bluyl)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No expenses found for this period.")

with col_right:
    st.subheader("Net Savings Trend")
    trend_df = db.get_monthly_savings_trend()
    if not trend_df.empty:
        fig_line = px.line(trend_df, x='month', y='savings', markers=True)
        fig_line.update_traces(line_color='#00FF00')
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No data available for trends.")

st.sidebar.markdown("---")
st.sidebar.info("Use the side menu to navigate to Transactions, Budgets, or Import/Export.")
