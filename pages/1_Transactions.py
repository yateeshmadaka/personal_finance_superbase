import streamlit as st
import db_manager as db
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="Transactions", page_icon="💳", layout="wide")

st.title("💳 Transactions Management")

# Initialize session state for person
if 'last_person' not in st.session_state:
    st.session_state.last_person = "Yateesh"

def format_currency(amount):
    return f"₹ {amount:,.0f}"

tab_expenses, tab_revenue = st.tabs(["💸 Expenses", "💰 Revenue"])

# --- EXPENSES TAB ---
with tab_expenses:
    st.subheader("Add New Expense")
    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            e_date = st.date_input("Date", value=date.today(), key="e_date")
            e_type = st.selectbox("Category", ["Groceries", "Rent", "Transport", "Utilities", "Dining Out", "Entertainment", "Health", "Shopping", "Other"], key="e_type")
        with col2:
            e_amount = st.number_input("Amount (INR)", min_value=0.0, step=100.0, key="e_amount")
            e_comments = st.text_input("Comments", key="e_comments")
        with col3:
            # Person selection
            e_person = st.selectbox("Person", ["Yateesh", "Prasanna"], index=["Yateesh", "Prasanna"].index(st.session_state.last_person), key="e_person")
        
        submitted_e = st.form_submit_button("Add Expense")
        if submitted_e:
            if e_amount > 0:
                db.add_expense(e_date, e_amount, e_type, e_comments, e_person)
                # Update session state
                st.session_state.last_person = e_person
                st.success(f"Expense added for {e_person}!")
                st.rerun()
            else:
                st.error("Amount must be positive.")

    st.subheader("Expense History")
    # Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        start_date = st.date_input("From", value=date(date.today().year, date.today().month, 1), key="e_start")
    with col_f2:
        end_date = st.date_input("To", value=date.today(), key="e_end")
        
    e_df = db.get_expenses(start_date, end_date)
    
    if not e_df.empty:
        # Display data with format
        display_df = e_df.copy()
        display_df['amount'] = display_df['amount'].apply(lambda x: format_currency(x))
        # Ensure person column is displayed
        if 'person' not in display_df.columns:
             display_df['person'] = "Unknown"
             
        st.dataframe(display_df, use_container_width=True)
        
        # Delete Action
        st.caption("To delete a record, enter its ID below.")
        with st.form("delete_expense_form"):
            del_id = st.number_input("ID to Delete", min_value=0, step=1)
            del_submit = st.form_submit_button("Delete Record")
            if del_submit:
                db.delete_expense(del_id)
                st.success(f"Expense {del_id} deleted.")
                st.rerun()
    else:
        st.info("No expenses found for this period.")

    st.divider()
    st.subheader("Edit Expense")
    with st.expander("Edit an existing expense"):
        edit_id = st.number_input("Enter Expense ID to Edit", min_value=1, step=1, key="edit_e_id")
        if st.button("Fetch Expense Details", key="fetch_e"):
            e_data = db.get_expense_by_id(edit_id)
            if not e_data.empty:
                st.session_state.edit_e_data = e_data.iloc[0]
                st.success("Expense found!")
            else:
                st.error("Expense ID not found.")
        
        if 'edit_e_data' in st.session_state:
            curr_e = st.session_state.edit_e_data
            # Check if the fetched ID matches the input ID (in case user changed input but didn't click fetch)
            if curr_e['id'] == edit_id:
                with st.form("edit_expense_form"):
                    # Pre-fill values
                    # Handle date conversion if needed (pandas timestamp to date)
                    curr_date = curr_e['date']
                    if isinstance(curr_date, str):
                        curr_date = datetime.strptime(curr_date, '%Y-%m-%d').date()
                    elif isinstance(curr_date, datetime): # Pandas Timestamp
                        curr_date = curr_date.date()
                        
                    new_e_date = st.date_input("Date", value=curr_date)
                    
                    # Category index
                    options = ["Groceries", "Rent", "Transport", "Utilities", "Dining Out", "Entertainment", "Health", "Shopping", "Other"]
                    try:
                        cat_idx = options.index(curr_e['type'])
                    except ValueError:
                        cat_idx = 0
                    new_e_type = st.selectbox("Category", options, index=cat_idx)
                    
                    new_e_amount = st.number_input("Amount", min_value=0.0, value=float(curr_e['amount']), step=100.0)
                    new_e_comments = st.text_input("Comments", value=curr_e['comments'])
                    
                    p_options = ["Yateesh", "Prasanna"]
                    try:
                        p_idx = p_options.index(curr_e['person'])
                    except ValueError:
                        p_idx = 0
                    new_e_person = st.selectbox("Person", p_options, index=p_idx)
                    
                    if st.form_submit_button("Update Expense"):
                        db.update_expense(edit_id, new_e_date, new_e_amount, new_e_type, new_e_comments, new_e_person)
                        st.success("Expense updated successfully!")
                        del st.session_state.edit_e_data # Clear state
                        st.rerun()
            else:
                st.warning("ID changed. Please click 'Fetch Expense Details' again.")

# --- REVENUE TAB ---
with tab_revenue:
    st.subheader("Add New Revenue")
    with st.form("add_revenue_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            r_date = st.date_input("Date", value=date.today(), key="r_date")
            r_type = st.selectbox("Source", ["Salary", "Bonus", "Gift", "Investment", "Other"], key="r_type")
        with col2:
            r_amount = st.number_input("Amount (INR)", min_value=0.0, step=100.0, key="r_amount")
            r_comments = st.text_input("Comments", key="r_comments")
        with col3:
             r_person = st.selectbox("Person", ["Yateesh", "Prasanna"], index=["Yateesh", "Prasanna"].index(st.session_state.last_person), key="r_person")
        
        submitted_r = st.form_submit_button("Add Revenue")
        if submitted_r:
            if r_amount > 0:
                db.add_revenue(r_date, r_amount, r_type, r_comments, r_person)
                st.session_state.last_person = r_person
                st.success(f"Revenue added for {r_person}!")
                st.rerun()
            else:
                st.error("Amount must be positive.")

    st.subheader("Revenue History")
    col_rf1, col_rf2 = st.columns(2)
    with col_rf1:
        r_start_date = st.date_input("From", value=date(date.today().year, date.today().month, 1), key="r_start")
    with col_rf2:
        r_end_date = st.date_input("To", value=date.today(), key="r_end")
        
    r_df = db.get_revenue(r_start_date, r_end_date)
    
    if not r_df.empty:
        display_r_df = r_df.copy()
        display_r_df['amount'] = display_r_df['amount'].apply(lambda x: format_currency(x))
        if 'person' not in display_r_df.columns:
             display_r_df['person'] = "Unknown"
        st.dataframe(display_r_df, use_container_width=True)
        
        # Delete Action
        st.caption("To delete a record, enter its ID below.")
        with st.form("delete_revenue_form"):
            r_del_id = st.number_input("ID to Delete", min_value=0, step=1)
            r_del_submit = st.form_submit_button("Delete Record")
            if r_del_submit:
                db.delete_revenue(r_del_id)
                st.success(f"Revenue {r_del_id} deleted.")
                st.rerun()
    else:
        st.info("No revenue records found for this period.")

    st.divider()
    st.subheader("Edit Revenue")
    with st.expander("Edit an existing revenue"):
        edit_r_id = st.number_input("Enter Revenue ID to Edit", min_value=1, step=1, key="edit_r_id")
        if st.button("Fetch Revenue Details", key="fetch_r"):
            r_data = db.get_revenue_by_id(edit_r_id)
            if not r_data.empty:
                st.session_state.edit_r_data = r_data.iloc[0]
                st.success("Revenue found!")
            else:
                st.error("Revenue ID not found.")
        
        if 'edit_r_data' in st.session_state:
            curr_r = st.session_state.edit_r_data
            if curr_r['id'] == edit_r_id:
                with st.form("edit_revenue_form"):
                    curr_date = curr_r['date']
                    if isinstance(curr_date, str):
                        curr_date = datetime.strptime(curr_date, '%Y-%m-%d').date()
                    elif isinstance(curr_date, datetime):
                        curr_date = curr_date.date()
                        
                    new_r_date = st.date_input("Date", value=curr_date)
                    
                    options = ["Salary", "Bonus", "Gift", "Investment", "Other"]
                    try:
                        type_idx = options.index(curr_r['type'])
                    except ValueError:
                        type_idx = 0
                    new_r_type = st.selectbox("Source", options, index=type_idx)
                    
                    new_r_amount = st.number_input("Amount", min_value=0.0, value=float(curr_r['amount']), step=100.0)
                    new_r_comments = st.text_input("Comments", value=curr_r['comments'])
                    
                    p_options = ["Yateesh", "Prasanna"]
                    try:
                        p_idx = p_options.index(curr_r['person'])
                    except ValueError:
                        p_idx = 0
                    new_r_person = st.selectbox("Person", p_options, index=p_idx)
                    
                    if st.form_submit_button("Update Revenue"):
                        db.update_revenue(edit_r_id, new_r_date, new_r_amount, new_r_type, new_r_comments, new_r_person)
                        st.success("Revenue updated successfully!")
                        del st.session_state.edit_r_data
                        st.rerun()
            else:
                st.warning("ID changed. Please click 'Fetch Revenue Details' again.")
