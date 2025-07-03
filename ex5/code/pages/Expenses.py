import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from utils.database import get_db

st.set_page_config(
    page_title="ניהול הוצאות",
    page_icon="💰",
    layout="wide"
)

st.title("💰 ניהול הוצאות וספקים")

# Database connection
db = get_db()

# Sidebar menu
with st.sidebar:
    st.header("פעולות")
    main_option = st.radio(
        "בחר ניהול",
        ["הוצאות", "ספקים"]
    )
    
    if main_option == "הוצאות":
        operation = st.radio(
            "בחר פעולה",
            ["הצג הוצאות", "הוסף הוצאה", "עדכן הוצאה", "מחק הוצאה"],
            key="expense_operation"
        )
    else:
        operation = st.radio(
            "בחר פעולה",
            ["הצג ספקים", "הוסף ספק", "עדכן ספק", "מחק ספק"],
            key="supplier_operation"
        )
    
    if st.button("🏠 חזרה לתפריט ראשי"):
        st.switch_page("app.py")

# EXPENSE MANAGEMENT
if main_option == "הוצאות":
    if operation == "הצג הוצאות":
        st.subheader("📋 רשימת הוצאות")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.selectbox(
                "סינון לפי קטגוריה",
                ["הכל"] + db.execute_query("SELECT DISTINCT category FROM expense ORDER BY category")
            )
        
        # Query
        query = """
        SELECT 
            e.expenseid,
            e.description,
            e.category,
            s.suppliername,
            COUNT(t.transactionid) as transaction_count,
            COALESCE(SUM(t.amount), 0) as total_amount
        FROM expense e
        LEFT JOIN supplier s ON e.supplierid = s.supplierid
        LEFT JOIN transaction t ON e.expenseid = t.expenseid
        """
        
        if category_filter != "הכל":
            query += f" WHERE e.category = '{category_filter}'"
        
        query += " GROUP BY e.expenseid, e.description, e.category, s.suppliername ORDER BY e.expenseid"
        
        try:
            df = db.get_dataframe(query)
            
            if not df.empty:
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("סה״כ הוצאות", len(df))
                with col2:
                    st.metric("סה״כ סכום", f"${df['total_amount'].sum():,.2f}")
                with col3:
                    st.metric("ממוצע להוצאה", f"${df['total_amount'].mean():,.2f}")
                
                # Table
                st.dataframe(
                    df.rename(columns={
                        'expenseid': 'מספר הוצאה',
                        'description': 'תיאור',
                        'category': 'קטגוריה',
                        'suppliername': 'ספק',
                        'transaction_count': 'מספר עסקאות',
                        'total_amount': 'סכום כולל'
                    }),
                    use_container_width=True
                )
                
                # Charts
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.pie(df, values='total_amount', names='category', title='התפלגות לפי קטגוריה')
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig = px.bar(df.nlargest(10, 'total_amount'), x='description', y='total_amount', 
                                title='10 ההוצאות הגדולות ביותר')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("לא נמצאו הוצאות")
                
        except Exception as e:
            st.error(f"שגיאה: {e}")
    
    elif operation == "הוסף הוצאה":
        st.subheader("➕ הוספת הוצאה חדשה")
        
        with st.form("add_expense"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Get next ID
                try:
                    max_id = db.execute_query("SELECT COALESCE(MAX(expenseid), 0) + 1 as next_id FROM expense")[0]['next_id']
                    expense_id = st.number_input("מספר הוצאה", value=int(max_id), disabled=True)
                except:
                    expense_id = st.number_input("מספר הוצאה", min_value=1)
                
                description = st.text_input("תיאור", max_chars=100)
                
            with col2:
                category = st.text_input("קטגוריה", max_chars=15)
                
                # Get suppliers
                suppliers = db.execute_query("SELECT supplierid, suppliername FROM supplier ORDER BY suppliername")
                supplier_options = ["ללא ספק"] + [f"{s['supplierid']} - {s['suppliername']}" for s in suppliers]
                selected_supplier = st.selectbox("ספק", supplier_options)
            
            submitted = st.form_submit_button("הוסף הוצאה", type="primary")
            
            if submitted:
                if not description or not category:
                    st.error("חובה למלא תיאור וקטגוריה")
                else:
                    try:
                        supplier_id = None if selected_supplier == "ללא ספק" else int(selected_supplier.split(" - ")[0])
                        
                        query = """
                        INSERT INTO expense (expenseid, description, category, supplierid)
                        VALUES (%s, %s, %s, %s)
                        """
                        db.execute_query(query, (expense_id, description, category, supplier_id), fetch=False)
                        st.success("✅ ההוצאה נוספה בהצלחה!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ שגיאה: {e}")
    
    elif operation == "עדכן הוצאה":
        st.subheader("✏️ עדכון הוצאה")
        
        expenses = db.execute_query("SELECT expenseid, description, category FROM expense ORDER BY expenseid")
        
        if expenses:
            expense_options = [f"{e['expenseid']} - {e['description']} ({e['category']})" for e in expenses]
            selected = st.selectbox("בחר הוצאה לעדכון", expense_options)
            expense_id = int(selected.split(" - ")[0])
            
            # Get current details
            current = db.execute_query("SELECT * FROM expense WHERE expenseid = %s", (expense_id,))[0]
            
            with st.form("update_expense"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_description = st.text_input("תיאור חדש", value=current['description'])
                    
                with col2:
                    new_category = st.text_input("קטגוריה חדשה", value=current['category'])
                    
                    # Get suppliers
                    suppliers = db.execute_query("SELECT supplierid, suppliername FROM supplier ORDER BY suppliername")
                    supplier_options = ["ללא ספק"] + [f"{s['supplierid']} - {s['suppliername']}" for s in suppliers]
                    
                    current_supplier_index = 0
                    if current['supplierid']:
                        for i, opt in enumerate(supplier_options):
                            if str(current['supplierid']) in opt:
                                current_supplier_index = i
                                break
                    
                    selected_supplier = st.selectbox("ספק", supplier_options, index=current_supplier_index)
                
                submitted = st.form_submit_button("עדכן הוצאה", type="primary")
                
                if submitted:
                    try:
                        supplier_id = None if selected_supplier == "ללא ספק" else int(selected_supplier.split(" - ")[0])
                        
                        query = """
                        UPDATE expense 
                        SET description = %s, category = %s, supplierid = %s
                        WHERE expenseid = %s
                        """
                        db.execute_query(query, (new_description, new_category, supplier_id, expense_id), fetch=False)
                        st.success("✅ ההוצאה עודכנה בהצלחה!")
                    except Exception as e:
                        st.error(f"❌ שגיאה: {e}")
    
    elif operation == "מחק הוצאה":
        st.subheader("🗑️ מחיקת הוצאה")
        st.warning("⚠️ שים לב: לא ניתן למחוק הוצאה שקשורה לעסקאות!")
        
        expenses = db.execute_query("""
            SELECT e.expenseid, e.description, e.category, COUNT(t.transactionid) as trans_count
            FROM expense e
            LEFT JOIN transaction t ON e.expenseid = t.expenseid
            GROUP BY e.expenseid, e.description, e.category
            ORDER BY e.expenseid
        """)
        
        if expenses:
            deletable_expenses = [e for e in expenses if e['trans_count'] == 0]
            
            if deletable_expenses:
                expense_options = [f"{e['expenseid']} - {e['description']} ({e['category']})" for e in deletable_expenses]
                selected = st.selectbox("בחר הוצאה למחיקה", expense_options)
                expense_id = int(selected.split(" - ")[0])
                
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    if st.button("🗑️ מחק הוצאה", type="primary"):
                        try:
                            db.execute_query("DELETE FROM expense WHERE expenseid = %s", (expense_id,), fetch=False)
                            st.success("✅ ההוצאה נמחקה בהצלחה!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ שגיאה: {e}")
            else:
                st.info("אין הוצאות שניתן למחוק (כולן קשורות לעסקאות)")

# SUPPLIER MANAGEMENT
else:  # main_option == "ספקים"
    if operation == "הצג ספקים":
        st.subheader("📋 רשימת ספקים")
        
        query = """
        SELECT 
            s.supplierid,
            s.suppliername,
            s.contactdetails,
            s.address,
            COUNT(e.expenseid) as expense_count,
            COUNT(DISTINCT t.transactionid) as transaction_count,
            COALESCE(SUM(t.amount), 0) as total_amount
        FROM supplier s
        LEFT JOIN expense e ON s.supplierid = e.supplierid
        LEFT JOIN transaction t ON e.expenseid = t.expenseid
        GROUP BY s.supplierid, s.suppliername, s.contactdetails, s.address
        ORDER BY s.supplierid
        """
        
        try:
            df = db.get_dataframe(query)
            
            if not df.empty:
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("סה״כ ספקים", len(df))
                with col2:
                    st.metric("סה״כ סכום עסקאות", f"${df['total_amount'].sum():,.2f}")
                with col3:
                    active_suppliers = len(df[df['transaction_count'] > 0])
                    st.metric("ספקים פעילים", active_suppliers)
                
                # Table
                st.dataframe(
                    df.rename(columns={
                        'supplierid': 'מספר ספק',
                        'suppliername': 'שם ספק',
                        'contactdetails': 'פרטי קשר',
                        'address': 'כתובת',
                        'expense_count': 'מספר הוצאות',
                        'transaction_count': 'מספר עסקאות',
                        'total_amount': 'סכום כולל'
                    }),
                    use_container_width=True
                )
                
                # Chart
                fig = px.bar(df.nlargest(10, 'total_amount'), x='suppliername', y='total_amount',
                            title='10 הספקים הגדולים ביותר')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("לא נמצאו ספקים")
                
        except Exception as e:
            st.error(f"שגיאה: {e}")
    
    elif operation == "הוסף ספק":
        st.subheader("➕ הוספת ספק חדש")
        
        with st.form("add_supplier"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Get next ID
                try:
                    max_id = db.execute_query("SELECT COALESCE(MAX(supplierid), 0) + 1 as next_id FROM supplier")[0]['next_id']
                    supplier_id = st.number_input("מספר ספק", value=int(max_id), disabled=True)
                except:
                    supplier_id = st.number_input("מספר ספק", min_value=1)
                
                supplier_name = st.text_input("שם ספק", max_chars=15)
                
            with col2:
                contact_details = st.text_input("פרטי קשר", max_chars=50)
                address = st.text_input("כתובת", max_chars=50)
            
            submitted = st.form_submit_button("הוסף ספק", type="primary")
            
            if submitted:
                if not all([supplier_name, contact_details, address]):
                    st.error("חובה למלא את כל השדות")
                else:
                    try:
                        query = """
                        INSERT INTO supplier (supplierid, suppliername, contactdetails, address)
                        VALUES (%s, %s, %s, %s)
                        """
 #                       db
                        db.execute_query(query, (supplier_id, supplier_name, contact_details, address), fetch=False)
                        st.success("✅ הספק נוסף בהצלחה!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ שגיאה: {e}")
    
    elif operation == "עדכן ספק":
        st.subheader("✏️ עדכון ספק")
        
        suppliers = db.execute_query("SELECT supplierid, suppliername FROM supplier ORDER BY supplierid")
        
        if suppliers:
            supplier_options = [f"{s['supplierid']} - {s['suppliername']}" for s in suppliers]
            selected = st.selectbox("בחר ספק לעדכון", supplier_options)
            supplier_id = int(selected.split(" - ")[0])
            
            # Get current details
            current = db.execute_query("SELECT * FROM supplier WHERE supplierid = %s", (supplier_id,))[0]
            
            with st.form("update_supplier"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("שם חדש", value=current['suppliername'])
                    new_contact = st.text_input("פרטי קשר חדשים", value=current['contactdetails'])
                    
                with col2:
                    new_address = st.text_input("כתובת חדשה", value=current['address'])
                
                submitted = st.form_submit_button("עדכן ספק", type="primary")
                
                if submitted:
                    try:
                        query = """
                        UPDATE supplier 
                        SET suppliername = %s, contactdetails = %s, address = %s
                        WHERE supplierid = %s
                        """
                        db.execute_query(query, (new_name, new_contact, new_address, supplier_id), fetch=False)
                        st.success("✅ הספק עודכן בהצלחה!")
                    except Exception as e:
                        st.error(f"❌ שגיאה: {e}")
    
    elif operation == "מחק ספק":
        st.subheader("🗑️ מחיקת ספק")
        st.warning("⚠️ שים לב: לא ניתן למחוק ספק שקשור להוצאות!")
        
        suppliers = db.execute_query("""
            SELECT s.supplierid, s.suppliername, COUNT(e.expenseid) as expense_count
            FROM supplier s
            LEFT JOIN expense e ON s.supplierid = e.supplierid
            GROUP BY s.supplierid, s.suppliername
            ORDER BY s.supplierid
        """)
        
        if suppliers:
            deletable_suppliers = [s for s in suppliers if s['expense_count'] == 0]
            
            if deletable_suppliers:
                supplier_options = [f"{s['supplierid']} - {s['suppliername']}" for s in deletable_suppliers]
                selected = st.selectbox("בחר ספק למחיקה", supplier_options)
                supplier_id = int(selected.split(" - ")[0])
                
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    if st.button("🗑️ מחק ספק", type="primary"):
                        try:
                            db.execute_query("DELETE FROM supplier WHERE supplierid = %s", (supplier_id,), fetch=False)
                            st.success("✅ הספק נמחק בהצלחה!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ שגיאה: {e}")
            else:
                st.info("אין ספקים שניתן למחוק (כולם קשורים להוצאות)")