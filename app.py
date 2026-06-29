import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ==========================================
# 1. DATABASE SETUP
# ==========================================
def init_db():
    # Using 'with' automatically opens and safely closes the database connection
    with sqlite3.connect("expenses.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL
            )
        """)

# Initialize the database when the app loads
init_db()

# ==========================================
# 2. APP UI & LAYOUT
# ==========================================
# Set the page title and width
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="centered")

st.title("💰 Personal Expense Tracker")
st.write("Welcome! Manage your daily expenses easily.")

# Create 3 distinct tabs for navigation
tab1, tab2, tab3 = st.tabs(["➕ Add Expense", "📋 View Expenses", "📊 Dashboard"])

# --- TAB 1: ADD EXPENSE ---
with tab1:
    st.header("Add a New Expense")
    
    with st.form("expense_form", clear_on_submit=True):
        amount = st.number_input("Amount Spent ($)", min_value=0.01, format="%.2f")
        
        # 1. The magic parameter: accept_new_options=True
        # We also set index=None so it starts blank, showing the placeholder instructions.
        category = st.selectbox(
            "Category", 
            ["Food", "Rent", "Entertainment", "Utilities", "Shopping"],
            index=None,
            placeholder="Select from list or type a new one...",
            accept_new_options=True
        )
        
        description = st.text_input("Brief Description")
        
        submitted = st.form_submit_button("Save Expense")
        
        if submitted:
            # 2. Validation: Make sure they didn't submit a blank category
            if not category:
                st.error("⚠️ Please select or type a category.")
            else:
                date = datetime.now().strftime("%Y-%m-%d")
                
                # 3. Clean up the user's input just in case they typed messy spaces
                clean_category = category.strip().title() 
                
                with sqlite3.connect("expenses.db") as conn:
                    conn.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)", 
                                 (amount, clean_category, description, date))
                st.success(f"✅ Expense added successfully under '{clean_category}'!")

# --- TAB 2: VIEW EXPENSES ---
with tab2:
    st.header("All Expenses")
    
    # Read the SQLite table directly into a Pandas DataFrame
    with sqlite3.connect("expenses.db") as conn:
        df = pd.read_sql_query("SELECT id, date, category, description, amount FROM expenses ORDER BY date DESC", conn)
    
    if df.empty:
        st.info("📭 No expenses recorded yet.")
    else:
        # Streamlit automatically renders Pandas dataframes as beautiful, interactive web tables
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- TAB 3: DASHBOARD & CHART ---
with tab3:
    st.header("Spending Breakdown")
    
    with sqlite3.connect("expenses.db") as conn:
        df_chart = pd.read_sql_query("SELECT category, SUM(amount) as total FROM expenses GROUP BY category", conn)
        
    if df_chart.empty:
        st.info("⚠️ Add some expenses to see your chart!")
    else:
        # Reusing your Matplotlib skills, but passing the figure to Streamlit
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.pie(df_chart['total'], labels=df_chart['category'], autopct='%1.1f%%', 
               startangle=140, colors=['#ff9999','#6bbf75','#66b3ff','#99ff99','#ffcc99'])
        ax.set_title("Total Spending by Category", fontsize=14, weight="bold")
        
        # This command renders the Matplotlib chart on the web page
        st.pyplot(fig)