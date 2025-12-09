import streamlit as st
import db_manager as db
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Import / Export", page_icon="📤", layout="wide")

st.title("📤 Import / Export Data")

tab_import, tab_export = st.tabs(["📥 Import CSV", "📤 Export CSV"])

# --- IMPORT TAB ---
with tab_import:
    st.info("Upload a CSV file to import data. The CSV must have headers matching the target table.")
    
    target_table = st.selectbox("Select Target Table", ["expenses", "revenue", "budget"])
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:")
            st.dataframe(df.head())
            
            # Validation requirements
            required_cols = {
                "expenses": ["date", "amount", "type", "person"],
                "revenue": ["date", "amount", "type", "person"],
                "budget": ["month", "amount"]
            }
            
            cols = required_cols[target_table]
            
            # For backward compatibility, if person is missing in CSV, maybe default it? 
            # User requirement implies we want to track it, but maybe old CSVs don't have it.
            # Let's enforce it for new imports or default to "Unknown" if missing to rely on flexibility?
            # User prompt: "while entering... keep another data entry as person".
            # Strictly speaking, headers must match target table in this simplistic import logic.
            # I will relax the check: if 'person' is missing but needed, I'll warn or default.
            # But the prompt said "Import CSV... Preview... skip invalid".
            # Let's add 'person' to required cols for strictness OR handle it.
            # Let's stick to strict requirement for now to match the "required columns" logic I wrote earlier, 
            # or better, allow it to be optional and default to "Variable"?
            # Simplest for user experience: Optional.
            
            missing_cols = [c for c in cols if c not in df.columns and c != "person"]
            
            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
            else:
                if st.button("Confirm Import"):
                    success_count = 0
                    errors = []
                    
                    progress_bar = st.progress(0)
                    
                    for index, row in df.iterrows():
                        try:
                            # Parse based on table
                            if target_table == "expenses":
                                d_val = row['date']
                                amt = float(row['amount'])
                                typ = row['type']
                                comm = row.get('comments', '')
                                pers = row.get('person', 'Yateesh') # Default if missing
                                
                                if amt <= 0:
                                    raise ValueError("Amount must be positive")
                                
                                db.add_expense(d_val, amt, typ, comm, pers)
                                
                            elif target_table == "revenue":
                                d_val = row['date']
                                amt = float(row['amount'])
                                typ = row['type']
                                comm = row.get('comments', '')
                                pers = row.get('person', 'Yateesh')
                                
                                if amt <= 0:
                                    raise ValueError("Amount must be positive")
                                    
                                db.add_revenue(d_val, amt, typ, comm, pers)
                                
                            elif target_table == "budget":
                                m_val = row['month']
                                amt = float(row['amount'])
                                comm = row.get('comments', '')
                                
                                if amt <= 0:
                                    raise ValueError("Amount must be positive")
                                    
                                db.add_budget(m_val, amt, comm)
                            
                            success_count += 1
                        except Exception as e:
                            errors.append(f"Row {index+1}: {str(e)}")
                        
                        progress_bar.progress((index + 1) / len(df))
                        
                    st.success(f"Imported {success_count} rows successfully.")
                    if errors:
                        st.warning(f"Skipped {len(errors)} rows due to errors:")
                        for err in errors:
                            st.write(err)
                            
        except Exception as e:
            st.error(f"Error reading CSV: {e}")


# --- EXPORT TAB ---
with tab_export:
    st.subheader("Download Data")
    
    export_table = st.selectbox("Select Table to Export", ["expenses", "revenue", "budget"])
    
    if st.button("Generate CSV"):
        if export_table == "expenses":
            df = db.get_expenses()
        elif export_table == "revenue":
            df = db.get_revenue()
        else:
            df = db.get_budgets()
            
        date_str = datetime.now().strftime("%Y%m%d")
        csv = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label=f"Download {export_table}.csv",
            data=csv,
            file_name=f"{export_table}_{date_str}.csv",
            mime="text/csv",
        )
