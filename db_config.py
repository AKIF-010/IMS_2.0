import mysql.connector
from tkinter import messagebox

def get_db_connection():
    try:
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="#01#02#03abc",  # আপনার ডাটাবেসের পাসওয়ার্ড থাকলে এখানে দেবেন
            database="ims_ai_database"
        )
        return con
    except Exception as e:
        print(f"Database Connection Error: {e}")
        # messagebox.showerror("Database Error", f"Cannot connect to database:\n{e}")
        return None