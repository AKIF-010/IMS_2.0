import mysql.connector
import random
from datetime import datetime, timedelta

def create_database():
    try:
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="#01#02#03abc"
        )
        cur = con.cursor()

        cur.execute("CREATE DATABASE IF NOT EXISTS ims_ai_database")
        cur.execute("USE ims_ai_database")

        # ================= USERS =================
        cur.execute('''CREATE TABLE IF NOT EXISTS users(
            emp_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(100),
            role VARCHAR(50), 
            contact VARCHAR(20),
            salary VARCHAR(20),
            status VARCHAR(20)
        )''')

        # ================= SUPPLIERS =================
        cur.execute('''CREATE TABLE IF NOT EXISTS suppliers(
            supp_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            contact VARCHAR(20),
            address TEXT
        )''')

        # ================= CATEGORIES =================
        cur.execute('''CREATE TABLE IF NOT EXISTS categories(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE
        )''')

        # ================= BRANDS =================
        cur.execute('''CREATE TABLE IF NOT EXISTS brands(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE
        )''')

        # ================= PRODUCTS (UPDATED) =================
        cur.execute('''CREATE TABLE IF NOT EXISTS products(
            pid INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            description TEXT,
            category VARCHAR(50),
            brand VARCHAR(50),
            supplier VARCHAR(100),
            cost_price DECIMAL(10,2),
            sale_price DECIMAL(10,2),
            tax_vat DECIMAL(5,2) DEFAULT 0,
            stock INT,
            low_stock_alert INT DEFAULT 5,
            barcode VARCHAR(50),
            sku VARCHAR(50),
            status VARCHAR(20)
        )''')

        # ================= SALES =================
        cur.execute('''CREATE TABLE IF NOT EXISTS sales(
            invoice_no INT AUTO_INCREMENT PRIMARY KEY,
            emp_id INT,
            customer_name VARCHAR(100),
            customer_phone VARCHAR(20),
            sale_date DATE,
            sale_time TIME,
            sub_total DECIMAL(10,2),
            total_discount DECIMAL(10,2),
            total_vat DECIMAL(10,2),
            grand_total DECIMAL(10,2)
        )''')

        # ================= SALES ITEMS =================
        cur.execute('''CREATE TABLE IF NOT EXISTS sales_items(
            id INT AUTO_INCREMENT PRIMARY KEY,
            invoice_no INT,
            pid INT,
            qty INT,
            unit_price DECIMAL(10,2),
            total_price DECIMAL(10,2)
        )''')

        # ================= LOGIN LOGS =================
        cur.execute('''CREATE TABLE IF NOT EXISTS login_logs(
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            emp_id INT,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # ================= PURCHASES =================
        cur.execute('''CREATE TABLE IF NOT EXISTS purchases(
            purchase_id INT AUTO_INCREMENT PRIMARY KEY,
            supp_id INT,
            emp_id INT,
            purchase_date DATE,
            total_amount DECIMAL(10,2)
        )''')

        # ================= PURCHASE ITEMS =================
        cur.execute('''CREATE TABLE IF NOT EXISTS purchase_items(
            id INT AUTO_INCREMENT PRIMARY KEY,
            purchase_id INT,
            pid INT,
            qty INT,
            cost_price DECIMAL(10,2),
            total_price DECIMAL(10,2)
        )''')

        # ================= SETTINGS =================
        cur.execute('''CREATE TABLE IF NOT EXISTS settings(
            id INT PRIMARY KEY DEFAULT 1,
            shop_name VARCHAR(100),
            address TEXT,
            phone VARCHAR(20),
            default_vat DECIMAL(5,2)
        )''')

        # ================= DEFAULT SETTINGS =================
        cur.execute("SELECT * FROM settings WHERE id=1")
        if not cur.fetchone():
            cur.execute("INSERT INTO settings VALUES (1,'My Super Shop','Dhaka, Bangladesh','01700000000',5.00)")

        con.commit()

        # ================= DEFAULT ADMIN =================
        cur.execute("SELECT * FROM users WHERE email='admin@ims.com'")
        if not cur.fetchone():
            cur.execute("""
            INSERT INTO users (name, email, password, role, contact, status)
            VALUES ('System Admin','admin@ims.com','admin123','Admin','01700000000','Active')
            """)

        # ================= DEFAULT PRODUCTS (UNCHANGED) =================
        cur.execute("SELECT COUNT(*) FROM products")
        if cur.fetchone()[0] == 0:
            products_data = [
                ("Premium Rice (50kg)", "", "Grocery", "Fresh", "", 2500, 2800, 0, 150, 20, "", "", "Active"),
                ("Soyabean Oil (5L)", "", "Grocery", "Rupchanda", "", 750, 820, 5, 80, 15, "", "", "Active"),
                ("Lexus Biscuit", "", "Snacks", "Pran", "", 80, 100, 5, 300, 50, "", "", "Active"),
                ("Mineral Water (1L)", "", "Beverage", "Kinley", "", 20, 25, 0, 500, 100, "", "", "Active"),
                ("Washing Powder (1kg)", "", "Cleaning", "Surf Excel", "", 180, 220, 5, 45, 10, "", "", "Active")
            ]

            cur.executemany("""
            INSERT INTO products(name,description,category,brand,supplier,cost_price,sale_price,tax_vat,stock,low_stock_alert,barcode,sku,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, products_data)

        # ================= AI SALES DATA (UNCHANGED) =================
        cur.execute("SELECT COUNT(*) FROM sales")
        if cur.fetchone()[0] == 0:
            print("Generating AI training sales data...")
            for i in range(200):
                days = random.randint(1,90)
                sale_date = (datetime.now()-timedelta(days=days)).strftime('%Y-%m-%d')
                sale_time = datetime.now().strftime('%H:%M:%S')

                sub = random.randint(500,5000)
                vat = sub*0.05
                total = sub+vat

                cur.execute("""
                INSERT INTO sales(emp_id,sale_date,sale_time,sub_total,total_vat,grand_total)
                VALUES (1,%s,%s,%s,%s,%s)
                """,(sale_date,sale_time,sub,vat,total))

                inv = cur.lastrowid

                for _ in range(random.randint(1,3)):
                    pid = random.randint(1,5)
                    qty = random.randint(1,5)
                    cur.execute("INSERT INTO sales_items(invoice_no,pid,qty) VALUES (%s,%s,%s)",(inv,pid,qty))

        con.commit()
        print("Database Ready ✅")

    except Exception as e:
        print("Error:", e)

    finally:
        if con.is_connected():
            cur.close()
            con.close()

if __name__ == "__main__":
    create_database()