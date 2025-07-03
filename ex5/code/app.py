import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="מערכת ניהול פיננסי - מלון",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    .info-card {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 5px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1557a4;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🏨 מערכת ניהול פיננסי - מלון</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">ברוכים הבאים למערכת הניהול הפיננסי המתקדמת</p>', unsafe_allow_html=True)

# Current time
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.info(f"🕐 {current_time}")

st.markdown("---")

# Navigation menu
st.markdown("### 📋 תפריט ראשי")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("#### 🧾 ניהול עסקאות")
    st.markdown("ניהול מלא של כל העסקאות הפיננסיות במלון - CRUD מלא")
    if st.button("כניסה לניהול עסקאות", key="btn_transactions", use_container_width=True):
        st.switch_page("pages/Transactions.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("#### 💰 ניהול הוצאות")
    st.markdown("מעקב ובקרה על כל ההוצאות והספקים - CRUD מלא")
    if st.button("כניסה לניהול הוצאות", key="btn_expenses", use_container_width=True):
        st.switch_page("pages/Expenses.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("#### 💳 אמצעי תשלום")
    st.markdown("ניהול אמצעי תשלום וקישורם לעסקאות - CRUD מלא")
    if st.button("כניסה לאמצעי תשלום", key="btn_payments", use_container_width=True):
        st.switch_page("pages/Payment_Methods.py")
    st.markdown('</div>', unsafe_allow_html=True)

col4, col5 = st.columns(2)

with col4:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("#### 📊 שאילתות ודוחות")
    st.markdown("הצגת דוחות ושאילתות מתקדמות מהמערכת")
    if st.button("כניסה לשאילתות", key="btn_queries", use_container_width=True):
        st.switch_page("pages/Queries.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col5:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ פונקציות מיוחדות")
    st.markdown("הפעלת פונקציות ופרוצדורות מותאמות אישית")
    if st.button("כניסה לפונקציות", key="btn_functions", use_container_width=True):
        st.switch_page("pages/Functions.py")
    st.markdown('</div>', unsafe_allow_html=True)

# Quick statistics
st.markdown("---")
st.markdown("### 📈 סטטיסטיקות מהירות")

try:
    from utils.database import get_db
    db = get_db()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        count = db.execute_query("SELECT COUNT(*) as count FROM transaction")[0]['count']
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("סה״כ עסקאות", f"{count:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        sum_amount = db.execute_query("SELECT COALESCE(SUM(amount), 0) as sum FROM transaction")[0]['sum']
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("סכום כולל", f"${sum_amount:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        expense_count = db.execute_query("SELECT COUNT(*) as count FROM expense")[0]['count']
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("סה״כ הוצאות", f"{expense_count:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        supplier_count = db.execute_query("SELECT COUNT(*) as count FROM supplier")[0]['count']
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("סה״כ ספקים", f"{supplier_count:,}")
        st.markdown('</div>', unsafe_allow_html=True)
        
except Exception as e:
    st.warning("לא ניתן להציג סטטיסטיקות - בדוק את החיבור לבסיס הנתונים")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 2rem;'>
    <p>מערכת ניהול פיננסי - מלון | פותח עבור פרויקט בסיסי נתונים</p>
    <p>© 2024 כל הזכויות שמורות</p>
</div>
""", unsafe_allow_html=True)