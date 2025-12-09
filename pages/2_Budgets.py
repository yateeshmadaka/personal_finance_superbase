import streamlit as st
import db_manager as db
import pandas as pd
from datetime import date

st.set_page_config(page_title="Budgets", page_icon="📊", layout="wide")

st.title("📊 Budget Management")

def format_currency(amount):
    return f"₹ {amount:,.0f}"

# Add Budget Form
st.subheader("Set Monthly Budget")
with st.form("add_budget_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        # Generate month options for next 2 years
        current_year = date.today().year
        months_opts = []
        for y in range(current_year, current_year + 2):
            for m in range(1, 13):
                months_opts.append(f"{y}-{m:02d}")
        
        # Default to current month
        current_month_str = f"{current_year}-{date.today().month:02d}"
        default_idx = months_opts.index(current_month_str) if current_month_str in months_opts else 0
        
        b_month = st.selectbox("Month (YYYY-MM)", months_opts, index=default_idx)
    
    with col2:
        b_amount = st.number_input("Budget Amount (INR)", min_value=0.0, step=1000.0)
        b_comments = st.text_input("Comments")
        
    submitted = st.form_submit_button("Set Budget")
    
    if submitted:
        if b_amount > 0:
            # Check if budget exists is skipped for MVP as per plan, we rely on insert
            # Ideally we should update if exists.
            # db.add_budget just inserts.
            db.add_budget(b_month, b_amount, b_comments)
            st.success(f"Budget for {b_month} set to {format_currency(b_amount)}")
            st.rerun()
        else:
            st.error("Budget amount must be positive.")

# View Budgets
st.divider()
st.subheader("Budget History")

budgets_df = db.get_budgets()

if not budgets_df.empty:
    display_df = budgets_df.copy()
    display_df['amount'] = display_df['amount'].apply(lambda x: format_currency(x))
    st.dataframe(display_df, use_container_width=True)

    # Delete Action
    st.caption("To delete a budget, enter its ID below.")
    with st.form("delete_budget_form"):
        del_id = st.number_input("ID to Delete", min_value=0, step=1)
        del_submit = st.form_submit_button("Delete Budget")
        if del_submit:
            db.delete_budget(del_id)
            st.success(f"Budget {del_id} deleted.")
            st.rerun()
else:
    st.info("No budgets set yet.")

st.divider()
st.subheader("Edit Budget")
with st.expander("Edit an existing budget"):
    edit_b_id = st.number_input("Enter Budget ID to Edit", min_value=1, step=1, key="edit_b_id")
    if st.button("Fetch Budget Details", key="fetch_b"):
        b_data = db.get_budget_by_id(edit_b_id)
        if not b_data.empty:
            st.session_state.edit_b_data = b_data.iloc[0]
            st.success("Budget found!")
        else:
            st.error("Budget ID not found.")
    
    if 'edit_b_data' in st.session_state:
        curr_b = st.session_state.edit_b_data
        if curr_b['id'] == edit_b_id:
            with st.form("edit_budget_form"):
                # Month options again
                current_year = date.today().year
                months_opts = []
                for y in range(current_year - 1, current_year + 2): # Extended range
                    for m in range(1, 13):
                        months_opts.append(f"{y}-{m:02d}")
                
                try:
                    m_idx = months_opts.index(curr_b['month'])
                except ValueError:
                    # If month is not in list (e.g. old data), add it or default
                    months_opts.insert(0, curr_b['month'])
                    m_idx = 0
                
                new_b_month = st.selectbox("Month (YYYY-MM)", months_opts, index=m_idx)
                new_b_amount = st.number_input("Budget Amount", min_value=0.0, value=float(curr_b['amount']), step=1000.0)
                new_b_comments = st.text_input("Comments", value=curr_b['comments'])
                
                if st.form_submit_button("Update Budget"):
                    db.update_budget(edit_b_id, new_b_month, new_b_amount, new_b_comments)
                    st.success("Budget updated successfully!")
                    del st.session_state.edit_b_data
                    st.rerun()
        else:
            st.warning("ID changed. Please click 'Fetch Budget Details' again.")
