import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import get_db

st.set_page_config(
    page_title="שאילתות ודוחות",
    page_icon="📊",
    layout="wide"
)

st.title("📊 שאילתות ודוחות")

# Database connection
db = get_db()

# Sidebar
with st.sidebar:
    st.header("בחר שאילתה")
    query_option = st.selectbox(
        "שאילתות זמינות",
        [
            "הוצאות עם ספקים וסכומי עסקאות",
            "אמצעי תשלום בשימוש",
            "סה״כ הוצאות לפי ספק",
            "ספקים ומספר ההוצאות",
            "עסקאות ללא מיסים",
            "עסקאות מפורטות",
            "הספק עם הסכום הגבוה ביותר",
            "חשבוניות מ-30 הימים האחרונים",
            "חשבוניות עם סכום סופי",
            "עסקאות מעל סף",
            "ממוצע אחוז מס",
            "מיסים לפי עסקה",
            "5 הספקים המובילים"
        ]
    )
    
    if st.button("🏠 חזרה לתפריט ראשי"):
        st.switch_page("app.py")

# Execute selected query
if query_option == "הוצאות עם ספקים וסכומי עסקאות":
    st.subheader("📋 כל ההוצאות עם פרטי ספקים וסכומי עסקאות")
    
    query = """
    SELECT 
        E.ExpenseID,
        E.Description,
        E.Category,
        S.SupplierName,
        T.Amount
    FROM Expense E
    JOIN Supplier S ON E.SupplierID = S.SupplierID
    LEFT JOIN Transaction T ON E.ExpenseID = T.ExpenseID
    """
    
    try:
        df = db.get_dataframe(query)
        if not df.empty:
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("סה״כ הוצאות", len(df))
            with col2:
                st.metric("סה״כ סכום", f"${df['amount'].sum():,.2f}")
            with col3:
                st.metric("מספר ספקים", df['suppliername'].nunique())
            
            # Table
            st.dataframe(df, use_container_width=True)
            
            # Chart
            fig = px.sunburst(df, path=['category', 'suppliername'], values='amount', 
                            title='התפלגות הוצאות לפי קטגוריה וספק')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("לא נמצאו תוצאות")
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "אמצעי תשלום בשימוש":
    st.subheader("💳 כל אמצעי התשלום בשימוש בעסקאות")
    
    query = """
    SELECT 
        T.transactionid,
        T.date,
        PM.methodname,
        PM.methoddetails
    FROM transaction T
    JOIN "paymentMethodUsedInTransaction" U ON T.transactionid = U.transactionid
    JOIN paymentmethod PM ON U.paymentmethodid = PM.paymentmethodid
    ORDER BY T.date DESC
    """
    
    try:
        df = db.get_dataframe(query)
        if not df.empty:
            # Table
            st.dataframe(df, use_container_width=True)
            
            # Chart
            method_counts = df['methodname'].value_counts()
            fig = px.pie(values=method_counts.values, names=method_counts.index, 
                        title='התפלגות שימוש באמצעי תשלום')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("לא נמצאו תוצאות")
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "סה״כ הוצאות לפי ספק":
    st.subheader("💰 סה״כ הוצאות לפי ספק")
    
    query = """
    SELECT 
        S.SupplierName,
        SUM(T.Amount) AS TotalSpent
    FROM Supplier S
    JOIN Expense E ON S.SupplierID = E.SupplierID
    JOIN Transaction T ON E.ExpenseID = T.ExpenseID
    GROUP BY S.SupplierName
    ORDER BY TotalSpent DESC
    """
    
    try:
        df = db.get_dataframe(query)
        if not df.empty:
            # Table
            st.dataframe(df, use_container_width=True)
            
            # Chart
            fig = px.bar(df, x='suppliername', y='totalspent', 
                        title='סה״כ הוצאות לפי ספק',
                        labels={'totalspent': 'סכום כולל', 'suppliername': 'שם ספק'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("לא נמצאו תוצאות")
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "ספקים ומספר ההוצאות":
    st.subheader("📊 ספקים ומספר ההוצאות הקשורות")
    
    query = """
    SELECT 
        Supplier.SupplierName,
        COUNT(Expense.ExpenseID) AS TotalExpenses
    FROM Supplier
    LEFT JOIN Expense ON Supplier.SupplierID = Expense.SupplierID
    GROUP BY Supplier.SupplierName
    ORDER BY TotalExpenses DESC
    """
    
    try:
        df = db.get_dataframe(query)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            fig = px.bar(df, x='suppliername', y='totalexpenses',
                        title='מספר הוצאות לפי ספק')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("לא נמצאו תוצאות")
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "עסקאות ללא מיסים":
    st.subheader("🚫 עסקאות ללא מיסים")
    
    query = """
    SELECT T.transactionid, T.date, T.amount, T.status
    FROM transaction T
    LEFT JOIN "transactionHasTax" H ON T.transactionid = H.transactionid
    WHERE H.taxid IS NULL
    ORDER BY T.date DESC
    """
    
    try:
        df = db.get_dataframe(query)
        if not df.empty:
            st.warning(f"נמצאו {len(df)} עסקאות ללא מיסים")
            st.dataframe(df, use_container_width=True)
        else:
            st.success("כל העסקאות משויכות למיסים!")
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "עסקאות מפורטות":
    st.subheader("📋 עסקאות עם פרטים מלאים")
    
    query = """
    SELECT 
        T.TransactionID,
        T.Date,
        T.Amount,
        T.Status,
        E.Category,
        S.SupplierName,
        PM.MethodName
    FROM Transaction T
    LEFT JOIN Expense E ON T.ExpenseID = E.ExpenseID
    LEFT JOIN Supplier S ON E.SupplierID = S.SupplierID
    LEFT JOIN "paymentMethodUsedInTransaction" U ON T.TransactionID = U.TransactionID
    LEFT JOIN PaymentMethod PM ON U.PaymentMethodID = PM.PaymentMethodID
    ORDER BY T.Date DESC
    """
    
    try:
        df = db.get_dataframe(query)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("לא נמצאו תוצאות")
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "הספק עם הסכום הגבוה ביותר":
    st.subheader("🏆 הספק עם סכום העסקאות הגבוה ביותר")
    
    query = """
    SELECT SupplierName
    FROM (
        SELECT 
            S.SupplierName,
            SUM(T.Amount) AS Total
        FROM Supplier S
        JOIN Expense E ON S.SupplierID = E.SupplierID
        JOIN Transaction T ON T.ExpenseID = E.ExpenseID
        GROUP BY S.SupplierName
        ORDER BY Total DESC
        LIMIT 1
    ) AS TopSupplier
    """
    
    try:
        result = db.execute_query(query)
        if result:
            st.success(f"הספק המוביל: **{result[0]['suppliername']}**")
            
            # Show details
            details_query = """
            SELECT 
                S.SupplierName,
                SUM(T.Amount) AS Total,
                COUNT(T.TransactionID) AS TransactionCount,
                AVG(T.Amount) AS AvgAmount
            FROM Supplier S
            JOIN Expense E ON S.SupplierID = E.SupplierID
            JOIN Transaction T ON T.ExpenseID = E.ExpenseID
            GROUP BY S.SupplierName
            ORDER BY Total DESC
            LIMIT 5
            """
            df = db.get_dataframe(details_query)
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "חשבוניות מ-30 הימים האחרונים":
    st.subheader("📅 עסקאות מ-30 הימים האחרונים")
    
    query = """
    SELECT *
    FROM Transaction
    WHERE Date >= CURRENT_DATE - INTERVAL '30 days'
    ORDER BY Date DESC
    """
    
    try:
        df = db.get_dataframe(query)
        if not df.empty:
            st.metric("מספר עסקאות", len(df))
            st.dataframe(df, use_container_width=True)
            
            # Timeline chart
            fig = px.scatter(df, x='date', y='amount', size='amount', color='status',
                           title='ציר זמן של עסקאות')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("לא נמצאו עסקאות ב-30 הימים האחרונים")
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "חשבוניות עם סכום סופי":
    st.subheader("💵 חשבוניות עם סכום סופי (אחרי הנחה)")
    
    query = """
    SELECT 
        Invoice.InvoiceID,
        Transaction.Amount,
# המשך מהמקום שנקטע...
        Invoice.Discount,
        (Transaction.Amount - COALESCE(Invoice.Discount, 0)) AS FinalAmount
    FROM Invoice
    JOIN Transaction ON Invoice.TransactionID = Transaction.TransactionID
    ORDER BY Invoice.InvoiceID
    """
    
    try:
        df = db.get_dataframe(query)
        if not df.empty:
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("סה״כ חשבוניות", len(df))
            with col2:
                st.metric("סה״כ לפני הנחה", f"${df['amount'].sum():,.2f}")
            with col3:
                st.metric("סה״כ אחרי הנחה", f"${df['finalamount'].sum():,.2f}")
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("לא נמצאו חשבוניות")
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "עסקאות מעל סף":
    st.subheader("💸 עסקאות מעל סף מסוים")
    
    threshold = st.number_input("הזן סכום סף", min_value=0, value=10000, step=1000)
    
    query = f"""
    SELECT * 
    FROM Transaction
    WHERE Amount > {threshold}
    ORDER BY Amount DESC
    """
    
    try:
        df = db.get_dataframe(query)
        if not df.empty:
            st.metric(f"עסקאות מעל ${threshold:,}", len(df))
            st.dataframe(df, use_container_width=True)
            
            # Chart
            fig = px.bar(df, x='transactionid', y='amount', color='status',
                        title=f'עסקאות מעל ${threshold:,}')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"לא נמצאו עסקאות מעל ${threshold:,}")
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "ממוצע אחוז מס":
    st.subheader("📊 ממוצע אחוז המס")
    
    query = """
    SELECT AVG(Percentage) AS AvgTaxRate
    FROM Tax
    """
    
    try:
        result = db.execute_query(query)
        if result and result[0]['avgtaxrate']:
            avg_tax = float(result[0]['avgtaxrate'])
            st.metric("ממוצע אחוז מס", f"{avg_tax:.2f}%")
            
            # Show tax distribution
            tax_dist_query = """
            SELECT percentage, COUNT(*) as count
            FROM Tax
            GROUP BY percentage
            ORDER BY percentage
            """
            df = db.get_dataframe(tax_dist_query)
            if not df.empty:
                fig = px.bar(df, x='percentage', y='count', 
                            title='התפלגות אחוזי מס')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("אין נתוני מס במערכת")
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "מיסים לפי עסקה":
    st.subheader("🧾 מיסים המוטלים על עסקאות")
    
    query = """
    SELECT 
        T.transactionid,
        T.amount as transaction_amount,
        Tax.taxamount,
        Tax.percentage,
        Tax.duedate
    FROM transaction T
    JOIN "transactionHasTax" H ON T.transactionid = H.transactionid
    JOIN tax ON H.taxid = Tax.taxid
    ORDER BY T.transactionid
    """
    
    try:
        df = db.get_dataframe(query)
        if not df.empty:
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("עסקאות עם מס", len(df))
            with col2:
                st.metric("סה״כ מס", f"${df['taxamount'].sum():,.2f}")
            with col3:
                st.metric("ממוצע מס לעסקה", f"${df['taxamount'].mean():,.2f}")
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("לא נמצאו עסקאות עם מס")
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif query_option == "5 הספקים המובילים":
    st.subheader("🏅 5 הספקים המובילים לפי מספר עסקאות")
    
    query = """
    SELECT 
        S.SupplierName,
        COUNT(T.TransactionID) AS TransactionCount
    FROM Supplier S
    JOIN Expense E ON S.SupplierID = E.SupplierID
    JOIN Transaction T ON E.ExpenseID = T.ExpenseID
    GROUP BY S.SupplierName
    ORDER BY TransactionCount DESC
    LIMIT 5
    """
    
    try:
        df = db.get_dataframe(query)
        if not df.empty:
            # Chart
            fig = go.Figure(data=[
                go.Bar(x=df['suppliername'], y=df['transactioncount'],
                      text=df['transactioncount'],
                      textposition='auto',
                      marker_color='lightblue')
            ])
            fig.update_layout(title='5 הספקים המובילים',
                            xaxis_title='שם ספק',
                            yaxis_title='מספר עסקאות')
            st.plotly_chart(fig, use_container_width=True)
            
            # Table
            st.dataframe(df, use_container_width=True)
        else:
            st.info("לא נמצאו נתונים")
    except Exception as e:
        st.error(f"שגיאה: {e}")