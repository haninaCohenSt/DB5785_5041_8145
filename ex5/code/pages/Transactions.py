import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from utils.database import get_db

st.set_page_config(
    page_title="ניהול עסקאות",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 ניהול עסקאות")

# Database connection
db = get_db()

# Sidebar menu
with st.sidebar:
    st.header("פעולות")
    operation = st.radio(
        "בחר פעולה",
        ["הצג עסקאות", "הוסף עסקה", "עדכן עסקה", "מחק עסקה", "קישור אמצעי תשלום"]
    )
    
    if st.button("🏠 חזרה לתפריט ראשי"):
        st.switch_page("app.py")

# Display transactions
if operation == "הצג עסקאות":
    st.subheader("📋 רשימת עסקאות")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "סינון לפי סטטוס",
            ["הכל", "Approved", "Pending", "Rejected"],
            key="status_filter"
        )
    with col2:
        date_from = st.date_input("מתאריך", value=date(2024, 1, 1))
    with col3:
        date_to = st.date_input("עד תאריך", value=date.today())
    
    # Query with joins
    query = """
    SELECT 
        t.transactionid,
        t.date,
        t.amount,
        t.status,
        e.description as expense_description,
        e.category as expense_category,
        s.suppliername,
        COUNT(pm.paymentmethodid) as payment_methods_count
    FROM transaction t
    LEFT JOIN expense e ON t.expenseid = e.expenseid
    LEFT JOIN supplier s ON e.supplierid = s.supplierid
    LEFT JOIN "paymentMethodUsedInTransaction" pmut ON t.transactionid = pmut.transactionid
    LEFT JOIN paymentmethod pm ON pmut.paymentmethodid = pm.paymentmethodid
    WHERE t.date BETWEEN %s AND %s
    """
    
    params = [date_from, date_to]
    
    if status_filter != "הכל":
        query += " AND t.status = %s"
        params.append(status_filter)
    
    query += " GROUP BY t.transactionid, t.date, t.amount, t.status, e.description, e.category, s.suppliername"
    query += " ORDER BY t.date DESC"
    
    try:
        df = db.get_dataframe(query, params)
        
        if not df.empty:
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("סה״כ עסקאות", len(df))
            with col2:
                st.metric("סכום כולל", f"${df['amount'].sum():,.2f}")
            with col3:
                st.metric("ממוצע לעסקה", f"${df['amount'].mean():,.2f}")
            with col4:
                approved = len(df[df['status'] == 'Approved'])
                st.metric("עסקאות מאושרות", approved)
            
            # Display table
            st.dataframe(
                df.rename(columns={
                    'transactionid': 'מספר עסקה',
                    'date': 'תאריך',
                    'amount': 'סכום',
                    'status': 'סטטוס',
                    'expense_description': 'תיאור הוצאה',
                    'expense_category': 'קטגוריה',
                    'suppliername': 'ספק',
                    'payment_methods_count': 'אמצעי תשלום'
                }),
                use_container_width=True
            )
            
            # Charts
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(df, values='amount', names='status', title='התפלגות לפי סטטוס')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                if 'expense_category' in df.columns and df['expense_category'].notna().any():
                    fig = px.bar(df[df['expense_category'].notna()].groupby('expense_category')['amount'].sum().reset_index(), 
                               x='expense_category', y='amount', title='סכום לפי קטגוריה')
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("לא נמצאו עסקאות בטווח התאריכים שנבחר")
            
    except Exception as e:
        st.error(f"שגיאה בשליפת נתונים: {e}")

# Add transaction
elif operation == "הוסף עסקה":
    st.subheader("➕ הוספת עסקה חדשה")
    
    with st.form("add_transaction", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Get next transaction ID
            try:
                max_id = db.execute_query("SELECT COALESCE(MAX(transactionid), 0) + 1 as next_id FROM transaction")[0]['next_id']
                transaction_id = st.number_input("מספר עסקה", value=int(max_id), disabled=True)
            except:
                transaction_id = st.number_input("מספר עסקה", min_value=1)
                
            amount = st.number_input("סכום", min_value=0.01, step=0.01)
            transaction_date = st.date_input("תאריך", value=date.today())
            
        with col2:
            status = st.selectbox("סטטוס", ["Approved", "Pending", "Rejected"])
            
            # Get expenses for dropdown
            expenses = db.execute_query("""
                SELECT e.expenseid, e.description, s.suppliername 
                FROM expense e
                LEFT JOIN supplier s ON e.supplierid = s.supplierid
                ORDER BY e.description
            """)
            
            expense_options = ["ללא הוצאה"] + [f"{exp['expenseid']} - {exp['description']} ({exp['suppliername'] or 'ללא ספק'})" for exp in expenses]
            selected_expense = st.selectbox("הוצאה קשורה", expense_options)
            
            # Get reservation ID (optional)
            reservation_id = st.number_input("מספר הזמנה (אופציונלי)", min_value=0, value=0)
            if reservation_id == 0:
                reservation_id = None
        
        submitted = st.form_submit_button("הוסף עסקה", type="primary")
        
        if submitted:
            try:
                expense_id = None if selected_expense == "ללא הוצאה" else int(selected_expense.split(" - ")[0])
                
                query = """
                INSERT INTO transaction (transactionid, date, amount, status, expenseid, reservation_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                db.execute_query(query, (transaction_id, transaction_date, amount, status, expense_id, reservation_id), fetch=False)
                st.success("✅ העסקה נוספה בהצלחה!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ שגיאה בהוספת עסקה: {e}")

# Update transaction  
elif operation == "עדכן עסקה":
    st.subheader("✏️ עדכון עסקה")
    
    # Get transactions for selection
    transactions = db.execute_query("""
        SELECT t.transactionid, t.amount, t.status, t.date, e.description
        FROM transaction t
        LEFT JOIN expense e ON t.expenseid = e.expenseid
        ORDER BY t.transactionid DESC
    """)
    
    if transactions:
        transaction_options = [f"{t['transactionid']} - ${t['amount']} - {t['status']} - {t['description'] or 'ללא הוצאה'}" for t in transactions]
        selected = st.selectbox("בחר עסקה לעדכון", transaction_options)
        transaction_id = int(selected.split(" - ")[0])
        
        # Get current transaction details
        current = db.execute_query(
            "SELECT * FROM transaction WHERE transactionid = %s",
            (transaction_id,)
        )[0]
        
        with st.form("update_transaction"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_amount = st.number_input("סכום חדש", value=float(current['amount']), step=0.01)
                new