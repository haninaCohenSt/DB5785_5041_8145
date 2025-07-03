import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from contextlib import contextmanager

class DatabaseConnection:
    def __init__(self):
        self.connection_params = {
            'host': st.secrets["postgres"]["host"],
            'port': st.secrets["postgres"]["port"],
            'database': st.secrets["postgres"]["database"],
            'user': st.secrets["postgres"]["user"],
            'password': st.secrets["postgres"]["password"]
        }
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and return results"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                else:
                    conn.commit()
                    return cur.rowcount
    
    def get_dataframe(self, query, params=None):
        """Get query results as pandas DataFrame"""
        results = self.execute_query(query, params)
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def call_function(self, func_name, params):
        """Call a database function"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                query = f"SELECT * FROM {func_name}(%s, %s)"
                cur.execute(query, params)
                return cur.fetchall()
    
    def call_procedure(self, proc_name, params):
        """Call a stored procedure with OUT parameters"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # For procedures with OUT parameters
                if proc_name == "process_monthly_taxes":
                    cur.execute("""
                        CALL process_monthly_taxes(%s, %s, NULL, NULL);
                        SELECT %s::INTEGER as processed_count, %s::NUMERIC as total_tax;
                    """, params + [0, 0])
                elif proc_name == "reconcile_reservations":
                    cur.execute("""
                        CALL reconcile_reservations(NULL, NULL, %s);
                        SELECT %s::INTEGER as created, %s::INTEGER as updated;
                    """, params + [0, 0])
                else:
                    cur.execute(f"CALL {proc_name}({','.join(['%s']*len(params))})", params)
                
                conn.commit()
                try:
                    return cur.fetchone() if cur.description else None
                except:
                    return None

# Create singleton instance
@st.cache_resource
def get_db():
    return DatabaseConnection()