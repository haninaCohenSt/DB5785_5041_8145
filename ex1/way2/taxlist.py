# import pg8000

# def insert_data():
#     # Database connection parameters
#     conn = pg8000.connect(
#         database="db5785_5041_8145",  # Changed 'dbname' to 'database'
#         user="postgres",
#         password="cohen",
#         host="172.17.0.2",
#         port=5432  # Changed from string to integer
#     )
    
#     # Create a cursor object
#     cur = conn.cursor()
    
#     # SQL statement to insert data
#     insert_query = """
#     INSERT INTO Tax (TaxID, Percentage, TaxAmount, DueDate)
#     VALUES (%s, %s, %s, %s)
#     """
    
#     # Data to be inserted
#     data = (1, 15.0, 100.0, '2025-12-31')
    
#     try:
#         # Execute the insert query
#         cur.execute(insert_query, data)
        
#         # Commit the transaction
#         conn.commit()
#         print("Data inserted successfully")
#     except Exception as e:
#         print("Error inserting data:", e)
#         conn.rollback()
#     finally:
#         # Close cursor and connection
#         cur.close()
#         conn.close()

# if __name__ == "__main__":
#     insert_data()



import pg8000
import random
import datetime

def insert_data():
    # Database connection parameters
    conn = pg8000.connect(
        database="db5785_5041_8145",  # Changed 'dbname' to 'database'
        user="postgres",
        password="cohen",
        host="172.17.0.2",
        port=5432  # Changed from string to integer
    )
    
    # Create a cursor object
    cur = conn.cursor()
    
    # SQL statement to insert data
    insert_query = """
    INSERT INTO Tax (TaxID, Percentage, TaxAmount, DueDate)
    VALUES (%s, %s, %s, %s)
    """
    
    try:
        for i in range(1, 401):  # Insert 400 random records
            tax_id = i
            percentage = round(random.uniform(5, 20), 2)  # Random percentage between 5% and 20%
            tax_amount = round(random.uniform(50, 500), 2)  # Random amount between 50 and 500
            due_date = datetime.date.today() + datetime.timedelta(days=random.randint(1, 365))  # Random due date within a year
            
            data = (tax_id, percentage, tax_amount, due_date)
            cur.execute(insert_query, data)
        
        # Commit the transaction
        conn.commit()
        print("400 random records inserted successfully")
    except Exception as e:
        print("Error inserting data:", e)
        conn.rollback()
    finally:
        # Close cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    insert_data()
