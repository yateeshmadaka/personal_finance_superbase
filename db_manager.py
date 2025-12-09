import psycopg2
import pandas as pd
from datetime import date, datetime
import streamlit as st
import os

# Supabase Connection
def get_connection():
    # Look for secrets in .streamlit/secrets.toml
    # Expected format:
    # [supabase]
    # host = "..."
    # database = "postgres"
    # user = "postgres"
    # password = "..."
    # port = 5432
    
    try:
        if 'supabase' in st.secrets:
            secrets = st.secrets['supabase']
            return psycopg2.connect(
                host=secrets['host'],
                database=secrets['database'],
                user=secrets['user'],
                password=secrets['password'],
                port=secrets['port']
            )
        else:
            # Fallback for local testing if env vars are set (optional)
            return psycopg2.connect(
                host=os.getenv("SUPABASE_HOST"),
                database=os.getenv("SUPABASE_DB"),
                user=os.getenv("SUPABASE_USER"),
                password=os.getenv("SUPABASE_PASS"),
                port=os.getenv("SUPABASE_PORT", 5432)
            )
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def init_db():
    con = get_connection()
    if not con:
        return
    
    cur = con.cursor()
    
    # Create tables if they don't exist
    # Postgres uses SERIAL for auto-increment
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            date DATE,
            amount DECIMAL,
            type TEXT,
            comments TEXT,
            person TEXT
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS revenue (
            id SERIAL PRIMARY KEY,
            date DATE,
            amount DECIMAL,
            type TEXT,
            comments TEXT,
            person TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id SERIAL PRIMARY KEY,
            month TEXT, -- YYYY-MM
            amount DECIMAL,
            comments TEXT
        );
    """)
    
    con.commit()
    cur.close()
    con.close()

# --- Expenses ---
def add_expense(date_val, amount, type_val, comments, person):
    con = get_connection()
    cur = con.cursor()
    query = """
    INSERT INTO expenses (date, amount, type, comments, person) 
    VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(query, (date_val, amount, type_val, comments, person))
    con.commit()
    cur.close()
    con.close()

def get_expenses(start_date=None, end_date=None):
    con = get_connection()
    query = "SELECT * FROM expenses"
    params = []
    
    if start_date and end_date:
        query += " WHERE date BETWEEN %s AND %s"
        params = [start_date, end_date]
        
    query += " ORDER BY date DESC"
    df = pd.read_sql(query, con, params=params)
    con.close()
    return df

def get_expense_by_id(expense_id):
    con = get_connection()
    query = "SELECT * FROM expenses WHERE id = %s"
    df = pd.read_sql(query, con, params=[expense_id])
    con.close()
    return df

def delete_expense(expense_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
    con.commit()
    cur.close()
    con.close()

def update_expense(expense_id, date_val, amount, type_val, comments, person):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        UPDATE expenses 
        SET date = %s, amount = %s, type = %s, comments = %s, person = %s
        WHERE id = %s
    """, (date_val, amount, type_val, comments, person, expense_id))
    con.commit()
    cur.close()
    con.close()


# --- Revenue ---
def add_revenue(date_val, amount, type_val, comments, person):
    con = get_connection()
    cur = con.cursor()
    query = """
    INSERT INTO revenue (date, amount, type, comments, person) 
    VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(query, (date_val, amount, type_val, comments, person))
    con.commit()
    cur.close()
    con.close()

def get_revenue(start_date=None, end_date=None):
    con = get_connection()
    query = "SELECT * FROM revenue"
    params = []
    if start_date and end_date:
        query += " WHERE date BETWEEN %s AND %s"
        params = [start_date, end_date]
    query += " ORDER BY date DESC"
    df = pd.read_sql(query, con, params=params)
    con.close()
    return df

def get_revenue_by_id(revenue_id):
    con = get_connection()
    query = "SELECT * FROM revenue WHERE id = %s"
    df = pd.read_sql(query, con, params=[revenue_id])
    con.close()
    return df

def delete_revenue(revenue_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM revenue WHERE id = %s", (revenue_id,))
    con.commit()
    cur.close()
    con.close()
    
def update_revenue(revenue_id, date_val, amount, type_val, comments, person):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        UPDATE revenue 
        SET date = %s, amount = %s, type = %s, comments = %s, person = %s
        WHERE id = %s
    """, (date_val, amount, type_val, comments, person, revenue_id))
    con.commit()
    cur.close()
    con.close()

# --- Budget ---
def add_budget(month_str, amount, comments):
    con = get_connection()
    cur = con.cursor()
    # Check if exists first to avoid duplicates or update?
    # For now, just insert as requested, but maybe unique constraint on month?
    # Let's stick to insert for now to match previous logic, but user can edit now.
    query = """
    INSERT INTO budget (month, amount, comments) 
    VALUES (%s, %s, %s)
    """
    cur.execute(query, (month_str, amount, comments))
    con.commit()
    cur.close()
    con.close()

def get_budgets():
    con = get_connection()
    df = pd.read_sql("SELECT * FROM budget ORDER BY month DESC", con)
    con.close()
    return df

def get_budget_by_id(budget_id):
    con = get_connection()
    query = "SELECT * FROM budget WHERE id = %s"
    df = pd.read_sql(query, con, params=[budget_id])
    con.close()
    return df

def delete_budget(budget_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM budget WHERE id = %s", (budget_id,))
    con.commit()
    cur.close()
    con.close()
    
def update_budget(budget_id, month_str, amount, comments):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        UPDATE budget 
        SET month = %s, amount = %s, comments = %s
        WHERE id = %s
    """, (month_str, amount, comments, budget_id))
    con.commit()
    cur.close()
    con.close()

# --- Dashboard Helpers ---
def get_monthly_summary(year, month):
    con = get_connection()
    if not con:
        return 0.0, 0.0, 0.0
    cur = con.cursor()
    month_str = f"{year}-{month:02d}"
    
    # Postgres: TO_CHAR(date, 'YYYY-MM')
    rev_query = """
        SELECT SUM(amount) FROM revenue 
        WHERE TO_CHAR(date, 'YYYY-MM') = %s
    """
    cur.execute(rev_query, (month_str,))
    res = cur.fetchone()
    total_rev = res[0] if res and res[0] else 0.0
    
    exp_query = """
        SELECT SUM(amount) FROM expenses 
        WHERE TO_CHAR(date, 'YYYY-MM') = %s
    """
    cur.execute(exp_query, (month_str,))
    res = cur.fetchone()
    total_exp = res[0] if res and res[0] else 0.0
    
    bud_query = "SELECT amount FROM budget WHERE month = %s"
    cur.execute(bud_query, (month_str,))
    res = cur.fetchone()
    budget_amt = res[0] if res and res[0] else 0.0
    
    cur.close()
    con.close()
    return float(total_rev), float(total_exp), float(budget_amt)
    
def get_monthly_savings_trend():
    con = get_connection()
    
    rev_df = pd.read_sql("""
        SELECT TO_CHAR(date, 'YYYY-MM') as month, SUM(amount) as revenue
        FROM revenue
        GROUP BY 1
    """, con)
    
    exp_df = pd.read_sql("""
        SELECT TO_CHAR(date, 'YYYY-MM') as month, SUM(amount) as expenses
        FROM expenses
        GROUP BY 1
    """, con)
    
    con.close()
    
    if rev_df.empty and exp_df.empty:
        return pd.DataFrame(columns=['month', 'savings'])
        
    df = pd.merge(rev_df, exp_df, on='month', how='outer').fillna(0)
    df['savings'] = df['revenue'] - df['expenses']
    df = df.sort_values('month')
    return df

def get_expense_breakdown(year, month):
    con = get_connection()
    month_str = f"{year}-{month:02d}"
    query = """
        SELECT type, SUM(amount) as total
        FROM expenses
        WHERE TO_CHAR(date, 'YYYY-MM') = %s
        GROUP BY type
        ORDER BY total DESC
    """
    df = pd.read_sql(query, con, params=[month_str])
    con.close()
    return df

# Initialize DB on import (only if secrets exist, otherwise might fail silently or log error)
try:
    init_db()
except Exception as e:
    pass # Will fail if secrets not set, expected during setup
