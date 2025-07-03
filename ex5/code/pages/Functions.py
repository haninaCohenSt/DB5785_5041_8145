import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from utils.database import get_db

st.set_page_config(
    page_title="פונקציות מיוחדות",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ פונקציות ופרוצדורות מיוחדות")

# Database connection
db = get_db()

# Sidebar
with st.sidebar:
    st.header("בחר פעולה")
    function_option = st.selectbox(
        "פונקציות זמינות",
        [
            "סיכום עסקאות לפי תקופה",
            "עסקאות ספק עם RefCursor",
            "עיבוד מיסים חודשי",
            "התאמת הזמנות"
        ]
    )
    
    if st.button("🏠 חזרה לתפריט ראשי"):
        st.switch_page("app.py")

if function_option == "סיכום עסקאות לפי תקופה":
    st.subheader("📊 סיכום עסקאות לפי תקופה")
    st.info("פונקציה זו מחשבת סיכום עסקאות לפי קטגוריות בטווח תאריכים נבחר")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("תאריך התחלה", value=date(2024, 1, 1))
    with col2:
        end_date = st.date_input("תאריך סיום", value=date.today())
    
    if st.button("הפעל פונקציה", type="primary"):
        try:
            # Call the function
            query = "SELECT * FROM calculate_transaction_summary(%s, %s)"
            results = db.execute_query(query, (start_date, end_date))
            
            if results:
                df = pd.DataFrame(results)
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("קטגוריות", len(df))
                with col2:
                    st.metric("סה״כ סכום", f"${df['total_amount'].sum():,.2f}")
                with col3:
                    st.metric("סה״כ עסקאות", df['transaction_count'].sum())
                with col4:
                    st.metric("סה״כ מס", f"${df['tax_total'].sum():,.2f}")
                
                # Display table
                st.dataframe(
                    df.rename(columns={
                        'category': 'קטגוריה',
                        'total_amount': 'סכום כולל',
                        'transaction_count': 'מספר עסקאות',
                        'avg_amount': 'ממוצע לעסקה',
                        'tax_total': 'סה״כ מס'
                    }),
                    use_container_width=True
                )
                
                # Charts
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.pie(df, values='total_amount', names='category', 
                                title='התפלגות סכומים לפי קטגוריה')
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig = px.bar(df, x='category', y='transaction_count', 
                                title='מספר עסקאות לפי קטגוריה')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("לא נמצאו עסקאות בתקופה הנבחרת")
                
        except Exception as e:
            st.error(f"שגיאה בהפעלת הפונקציה: {e}")

elif function_option == "עסקאות ספק עם RefCursor":
    st.subheader("🔍 עסקאות ספק - RefCursor")
    st.info("פונקציה זו מחזירה פרטי עסקאות מפורטים עבור ספק נבחר")
    
    # Get suppliers for dropdown
    suppliers = db.execute_query("SELECT supplierid, suppliername FROM supplier ORDER BY suppliername")
    
    if suppliers:
        supplier_options = [f"{s['supplierid']} - {s['suppliername']}" for s in suppliers]
        selected_supplier = st.selectbox("בחר ספק", supplier_options)
        supplier_id = int(selected_supplier.split(" - ")[0])
        
        if st.button("הצג עסקאות ספק", type="primary"):
            try:
                # Since RefCursor is complex in Python, we'll use a direct query instead
                query = """
                SELECT 
                    s.suppliername,
                    s.contactdetails,
                    e.description as expense_description,
                    e.category,
                    t.transactionid,
                    t.date as transaction_date,
                    t.amount,
                    t.status,
                    i.invoiceid,
                    i.discount,
                    CASE 
                        WHEN i.discount IS NOT NULL THEN 
                            ROUND(t.amount - (t.amount * i.discount / 100), 2)
                        ELSE t.amount
                    END as final_amount
                FROM supplier s
                JOIN expense e ON s.supplierid = e.supplierid
                JOIN transaction t ON e.expenseid = t.expenseid
                LEFT JOIN invoice i ON t.transactionid = i.transactionid
                WHERE s.supplierid = %s
                ORDER BY t.date DESC
                """
                
                df = db.get_dataframe(query, (supplier_id,))
                
                if not df.empty:
                    # Display supplier info
                    st.success(f"ספק: {df.iloc[0]['suppliername']} | פרטי קשר: {df.iloc[0]['contactdetails']}")
                    
                    # Metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("סה״כ עסקאות", len(df))
                    with col2:
                        # המשך מהמקום שנקטע...
                        st.metric("סכום כולל", f"${df['amount'].sum():,.2f}")
                    with col3:
                        st.metric("סכום סופי", f"${df['final_amount'].sum():,.2f}")
                    
                    # Display table
                    st.dataframe(
                        df.rename(columns={
                            'suppliername': 'שם ספק',
                            'contactdetails': 'פרטי קשר',
                            'expense_description': 'תיאור הוצאה',
                            'category': 'קטגוריה',
                            'transactionid': 'מספר עסקה',
                            'transaction_date': 'תאריך',
                            'amount': 'סכום',
                            'status': 'סטטוס',
                            'invoiceid': 'מספר חשבונית',
                            'discount': 'הנחה %',
                            'final_amount': 'סכום סופי'
                        }),
                        use_container_width=True
                    )
                    
                    # Chart
                    fig = px.line(df, x='transaction_date', y='amount', 
                                 title='היסטוריית עסקאות',
                                 markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("לא נמצאו עסקאות עבור ספק זה")
                    
            except Exception as e:
                st.error(f"שגיאה: {e}")
    else:
        st.info("לא נמצאו ספקים במערכת")

elif function_option == "עיבוד מיסים חודשי":
    st.subheader("📅 עיבוד מיסים חודשי")
    st.info("פרוצדורה זו מעבדת ומחשבת מיסים עבור כל העסקאות בחודש נבחר")
    
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox("בחר חודש", range(1, 13), format_func=lambda x: f"{x:02d}")
    with col2:
        year = st.number_input("בחר שנה", min_value=2020, max_value=2030, value=datetime.now().year)
    
    if st.button("הפעל עיבוד מיסים", type="primary"):
        try:
            # Call the procedure
            query = """
            DO $$
            DECLARE
                v_processed INTEGER;
                v_total_tax NUMERIC;
            BEGIN
                CALL process_monthly_taxes(%s, %s, v_processed, v_total_tax);
                INSERT INTO temp_result VALUES (v_processed, v_total_tax);
            END $$;
            SELECT * FROM temp_result;
            DROP TABLE IF EXISTS temp_result;
            """
            
            # Create temp table and execute
            db.execute_query("CREATE TEMP TABLE IF NOT EXISTS temp_result (processed INTEGER, total_tax NUMERIC)", fetch=False)
            db.execute_query(f"CALL process_monthly_taxes({month}, {year}, NULL, NULL)", fetch=False)
            
            st.success(f"✅ עיבוד המיסים לחודש {month}/{year} הושלם בהצלחה!")
            
            # Show results
            tax_query = """
            SELECT t.transactionid, t.amount, tx.taxamount, tx.percentage, tx.duedate
            FROM transaction t
            JOIN "transactionHasTax" tht ON t.transactionid = tht.transactionid
            JOIN tax tx ON tht.taxid = tx.taxid
            WHERE EXTRACT(MONTH FROM t.date) = %s AND EXTRACT(YEAR FROM t.date) = %s
            ORDER BY t.transactionid DESC
            """
            
            df = db.get_dataframe(tax_query, (month, year))
            
            if not df.empty:
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("עסקאות עובדו", len(df))
                with col2:
                    st.metric("סה״כ מס", f"${df['taxamount'].sum():,.2f}")
                with col3:
                    st.metric("ממוצע מס", f"${df['taxamount'].mean():,.2f}")
                
                st.dataframe(df, use_container_width=True)
            else:
                st.info("לא נמצאו עסקאות לעיבוד בחודש זה")
                
        except Exception as e:
            st.error(f"שגיאה בעיבוד מיסים: {e}")

elif function_option == "התאמת הזמנות":
    st.subheader("🔄 התאמת הזמנות")
    st.info("פרוצדורה זו מסנכרנת הזמנות עם עסקאות פיננסיות")
    
    sync_days = st.number_input("מספר ימים אחורה לסנכרון", min_value=1, max_value=365, value=7)
    
    # Display current unlinked reservations
    unlinked_query = """
    SELECT rs.*
    FROM reservationsync rs
    LEFT JOIN reservationfinancelink rfl ON rs.reservation_id = rfl.reservation_id
    WHERE rfl.link_id IS NULL
    AND rs.sync_date >= CURRENT_DATE - INTERVAL '%s days'
    """
    
    try:
        unlinked_df = db.get_dataframe(unlinked_query, (sync_days,))
        
        if not unlinked_df.empty:
            st.warning(f"נמצאו {len(unlinked_df)} הזמנות לא מקושרות")
            
            with st.expander("הצג הזמנות לא מקושרות"):
                st.dataframe(unlinked_df, use_container_width=True)
        else:
            st.success("כל ההזמנות מקושרות!")
        
        if st.button("הפעל התאמת הזמנות", type="primary"):
            try:
                # Call the procedure
                db.execute_query(f"CALL reconcile_reservations(NULL, NULL, {sync_days})", fetch=False)
                
                st.success("✅ התאמת ההזמנות הושלמה בהצלחה!")
                
                # Show results from sync log
                log_query = """
                SELECT * FROM reservation_sync_log
                WHERE process_timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 minute'
                ORDER BY process_timestamp DESC
                """
                
                log_df = db.get_dataframe(log_query)
                
                if not log_df.empty:
                    st.subheader("יומן פעולות")
                    st.dataframe(log_df, use_container_width=True)
                    
                    # Summary metrics
                    created = len(log_df[log_df['operation_type'] == 'CREATE_TRANSACTION'])
                    updated = len(log_df[log_df['operation_type'] == 'UPDATE_TRANSACTION'])
                    errors = len(log_df[log_df['sync_status'] == 'FAILED'])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("עסקאות נוצרו", created)
                    with col2:
                        st.metric("עסקאות עודכנו", updated)
                    with col3:
                        st.metric("שגיאות", errors)
                
                st.rerun()
                
            except Exception as e:
                st.error(f"שגיאה בהתאמת הזמנות: {e}")
                
    except Exception as e:
        st.error(f"שגיאה: {e}")

# Footer with information
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>פונקציות ופרוצדורות אלו נוצרו במיוחד עבור המערכת הפיננסית</p>
    <p>הן מאפשרות ביצוע פעולות מורכבות בצורה אוטומטית ויעילה</p>
</div>
""", unsafe_allow_html=True)