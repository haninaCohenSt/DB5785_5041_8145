import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_db

st.set_page_config(
    page_title="אמצעי תשלום",
    page_icon="💳",
    layout="wide"
)

st.title("💳 ניהול אמצעי תשלום")

# Database connection
db = get_db()

# Sidebar menu
with st.sidebar:
    st.header("פעולות")
    operation = st.radio(
        "בחר פעולה",
        ["הצג אמצעי תשלום", "הוסף אמצעי תשלום", "עדכן אמצעי תשלום", "מחק אמצעי תשלום", "קישור לעסקאות"]
    )
    
    if st.button("🏠 חזרה לתפריט ראשי"):
        st.switch_page("app.py")

if operation == "הצג אמצעי תשלום":
    st.subheader("📋 רשימת אמצעי תשלום")
    
    query = """
    SELECT 
        pm.paymentmethodid,
        pm.methodname,
        pm.methoddetails,
        COUNT(DISTINCT pmut.transactionid) as transaction_count,
        COALESCE(SUM(t.amount), 0) as total_amount
    FROM paymentmethod pm
    LEFT JOIN "paymentMethodUsedInTransaction" pmut ON pm.paymentmethodid = pmut.paymentmethodid
    LEFT JOIN transaction t ON pmut.transactionid = t.transactionid
    GROUP BY pm.paymentmethodid, pm.methodname, pm.methoddetails
    ORDER BY pm.paymentmethodid
    """
    
    try:
        df = db.get_dataframe(query)
        
        if not df.empty:
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("סה״כ אמצעי תשלום", len(df))
            with col2:
                st.metric("סה״כ סכום עסקאות", f"${df['total_amount'].sum():,.2f}")
            with col3:
                active_methods = len(df[df['transaction_count'] > 0])
                st.metric("אמצעים פעילים", active_methods)
            
            # Table
            st.dataframe(
                df.rename(columns={
                    'paymentmethodid': 'מספר אמצעי',
                    'methodname': 'שם האמצעי',
                    'methoddetails': 'פרטים',
                    'transaction_count': 'מספר עסקאות',
                    'total_amount': 'סכום כולל'
                }),
                use_container_width=True
            )
            
            # Charts
            if df['transaction_count'].sum() > 0:
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.pie(df[df['transaction_count'] > 0], values='transaction_count', names='methodname', 
                                title='התפלגות עסקאות לפי אמצעי תשלום')
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig = px.bar(df, x='methodname', y='total_amount', title='סכום עסקאות לפי אמצעי תשלום')
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("לא נמצאו אמצעי תשלום")
            
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif operation == "הוסף אמצעי תשלום":
    st.subheader("➕ הוספת אמצעי תשלום חדש")
    
    with st.form("add_payment_method"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Get next ID
            try:
                max_id = db.execute_query("SELECT COALESCE(MAX(paymentmethodid), 0) + 1 as next_id FROM paymentmethod")[0]['next_id']
                method_id = st.number_input("מספר אמצעי", value=int(max_id), disabled=True)
            except:
                method_id = st.number_input("מספר אמצעי", min_value=1)
            
            method_name = st.text_input("שם האמצעי", max_chars=15)
            
        with col2:
            method_details = st.text_input("פרטים", max_chars=50, value="USD")
        
        submitted = st.form_submit_button("הוסף אמצעי תשלום", type="primary")
        
        if submitted:
            if not method_name:
                st.error("חובה למלא שם אמצעי")
            else:
                try:
                    query = """
                    INSERT INTO paymentmethod (paymentmethodid, methodname, methoddetails)
                    VALUES (%s, %s, %s)
                    """
                    db.execute_query(query, (method_id, method_name, method_details), fetch=False)
                    st.success("✅ אמצעי התשלום נוסף בהצלחה!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ שגיאה: {e}")

elif operation == "עדכן אמצעי תשלום":
    st.subheader("✏️ עדכון אמצעי תשלום")
    
    methods = db.execute_query("SELECT paymentmethodid, methodname FROM paymentmethod ORDER BY paymentmethodid")
    
    if methods:
        method_options = [f"{m['paymentmethodid']} - {m['methodname']}" for m in methods]
        selected = st.selectbox("בחר אמצעי לעדכון", method_options)
        method_id = int(selected.split(" - ")[0])
        
        # Get current details
        current = db.execute_query("SELECT * FROM paymentmethod WHERE paymentmethodid = %s", (method_id,))[0]
        
        with st.form("update_payment_method"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("שם חדש", value=current['methodname'])
                
            with col2:
                new_details = st.text_input("פרטים חדשים", value=current['methoddetails'] or "")
            
            submitted = st.form_submit_button("עדכן אמצעי תשלום", type="primary")
            
            if submitted:
                try:
                    query = """
                    UPDATE paymentmethod 
                    SET methodname = %s, methoddetails = %s
                    WHERE paymentmethodid = %s
                    """
                    db.execute_query(query, (new_name, new_details, method_id), fetch=False)
                    st.success("✅ אמצעי התשלום עודכן בהצלחה!")
                except Exception as e:
                    st.error(f"❌ שגיאה: {e}")

elif operation == "מחק אמצעי תשלום":
    st.subheader("🗑️ מחיקת אמצעי תשלום")
    st.warning("⚠️ שים לב: לא ניתן למחוק אמצעי תשלום שקשור לעסקאות!")
    
    methods = db.execute_query("""
        SELECT pm.paymentmethodid, pm.methodname, COUNT(pmut.transactionid) as trans_count
        FROM paymentmethod pm
        LEFT JOIN "paymentMethodUsedInTransaction" pmut ON pm.paymentmethodid = pmut.paymentmethodid
        GROUP BY pm.paymentmethodid, pm.methodname
        ORDER BY pm.paymentmethodid
    """)
    
    if methods:
        deletable_methods = [m for m in methods if m['trans_count'] == 0]
        
        if deletable_methods:
            method_options = [f"{m['paymentmethodid']} - {m['methodname']}" for m in deletable_methods]
            selected = st.selectbox("בחר אמצעי למחיקה", method_options)
            method_id = int(selected.split(" - ")[0])
            
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                if st.button("🗑️ מחק אמצעי", type="primary"):
                    try:
                        db.execute_query("DELETE FROM paymentmethod WHERE paymentmethodid = %s", (method_id,), fetch=False)
                        st.success("✅ אמצעי התשלום נמחק בהצלחה!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ שגיאה: {e}")
        else:
            st.info("אין אמצעי תשלום שניתן למחוק (כולם קשורים לעסקאות)")

elif operation == "קישור לעסקאות":
    st.subheader("🔗 קישור אמצעי תשלום לעסקאות")
    
    # This is the linking table - demonstrates M:N relationship
    tab1, tab2 = st.tabs(["הוסף קישור", "הצג קישורים"])
    
    with tab1:
        with st.form("link_payment_to_transaction"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Get transactions
                transactions = db.execute_query("""
                    SELECT t.transactionid, t.amount, t.date, t.status
                    FROM transaction t
                    ORDER BY t.transactionid DESC
                """)
                trans_options = [f"{t['transactionid']} - ${t['amount']} - {t['date']}" for t in transactions]
                selected_trans = st.selectbox("בחר עסקה", trans_options)
                
            with col2:
                # Get payment methods
                methods = db.execute_query("SELECT paymentmethodid, methodname FROM paymentmethod ORDER BY methodname")
                method_options = [f"{m['paymentmethodid']} - {m['methodname']}" for m in methods]
# המשך מהמקום שנקטע...
                selected_method = st.selectbox("בחר אמצעי תשלום", method_options)
            
            submitted = st.form_submit_button("צור קישור", type="primary")
            
            if submitted:
                try:
                    trans_id = int(selected_trans.split(" - ")[0])
                    method_id = int(selected_method.split(" - ")[0])
                    
                    # Check if link already exists
                    existing = db.execute_query("""
                        SELECT * FROM "paymentMethodUsedInTransaction" 
                        WHERE transactionid = %s AND paymentmethodid = %s
                    """, (trans_id, method_id))
                    
                    if existing:
                        st.warning("קישור זה כבר קיים!")
                    else:
                        query = """
                        INSERT INTO "paymentMethodUsedInTransaction" (transactionid, paymentmethodid)
                        VALUES (%s, %s)
                        """
                        db.execute_query(query, (trans_id, method_id), fetch=False)
                        st.success("✅ הקישור נוצר בהצלחה!")
                except Exception as e:
                    st.error(f"❌ שגיאה: {e}")
    
    with tab2:
        # Show existing links
        links_query = """
        SELECT 
            t.transactionid,
            t.amount,
            t.date,
            pm.methodname,
            pm.methoddetails
        FROM "paymentMethodUsedInTransaction" pmut
        JOIN transaction t ON pmut.transactionid = t.transactionid
        JOIN paymentmethod pm ON pmut.paymentmethodid = pm.paymentmethodid
        ORDER BY t.date DESC
        """
        
        links_df = db.get_dataframe(links_query)
        
        if not links_df.empty:
            st.dataframe(
                links_df.rename(columns={
                    'transactionid': 'מספר עסקה',
                    'amount': 'סכום',
                    'date': 'תאריך',
                    'methodname': 'אמצעי תשלום',
                    'methoddetails': 'פרטים'
                }),
                use_container_width=True
            )
        else:
            st.info("אין קישורים קיימים")