"""
database.py
-----------
Yeh file SQLite database ko manage karti hai.
Beginner ke liye: SQLite ek chhota database hai jo ek file (.db) mein
saara data save karta hai. Isko install karne ki zaroorat nahi,
Python ke andar hi built-in hota hai.

Is file mein hum:
1. Database se connect karte hain
2. Zaroori tables banate hain (agar pehle se nahi hain)
3. Products aur Sales ke liye CRUD (Create, Read, Update, Delete) functions likhte hain
"""

import sqlite3
from datetime import datetime

DB_NAME = "smart_shop.db"


def get_connection():
    """Database se connection banata hai aur return karta hai."""
    conn = sqlite3.connect(DB_NAME)
    # Foreign key checks on rakhte hain (products aur sales ko jodne ke liye)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Agar tables pehle se exist nahi karte, to yeh function unhe create kar deta hai.
    Yeh app start hote hi ek baar call hota hai.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ---------- PRODUCTS TABLE ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            purchase_price REAL NOT NULL CHECK (purchase_price >= 0),
            selling_price REAL NOT NULL CHECK (selling_price >= 0),
            current_stock INTEGER NOT NULL CHECK (current_stock >= 0),
            min_stock INTEGER NOT NULL CHECK (min_stock >= 0),
            supplier TEXT,
            date_added TEXT NOT NULL
        )
    """)

    # ---------- SALES TABLE ----------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            selling_price REAL NOT NULL CHECK (selling_price >= 0),
            total_amount REAL NOT NULL,
            sale_date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
#                    PRODUCT FUNCTIONS
# ============================================================

def add_product(name, category, purchase_price, selling_price,
                 current_stock, min_stock, supplier):
    """Naya product database mein add karta hai."""
    conn = get_connection()
    cursor = conn.cursor()
    date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO products
        (name, category, purchase_price, selling_price, current_stock, min_stock, supplier, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, category, purchase_price, selling_price, current_stock, min_stock, supplier, date_added))
    conn.commit()
    conn.close()


def get_all_products():
    """Saare products ki list deta hai."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_product_by_id(product_id):
    """Ek specific product ki details deta hai."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def search_products(keyword):
    """Naam ya category se product search karta hai."""
    conn = get_connection()
    cursor = conn.cursor()
    like_keyword = f"%{keyword}%"
    cursor.execute("""
        SELECT * FROM products
        WHERE name LIKE ? OR category LIKE ?
        ORDER BY name
    """, (like_keyword, like_keyword))
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_product(product_id, name, category, purchase_price, selling_price, min_stock, supplier):
    """Product ki details update karta hai (stock alag se update hota hai)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name = ?, category = ?, purchase_price = ?, selling_price = ?, min_stock = ?, supplier = ?
        WHERE product_id = ?
    """, (name, category, purchase_price, selling_price, min_stock, supplier, product_id))
    conn.commit()
    conn.close()


def update_stock(product_id, new_stock):
    """Product ka stock value directly set karta hai."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET current_stock = ? WHERE product_id = ?", (new_stock, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id):
    """Product ko database se delete karta hai."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()


def get_low_stock_products():
    """Woh products jinka stock minimum level se kam ya barabar hai."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products WHERE current_stock <= min_stock AND current_stock > 0
        ORDER BY current_stock ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_out_of_stock_products():
    """Woh products jinka stock zero hai."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE current_stock = 0")
    rows = cursor.fetchall()
    conn.close()
    return rows


# ============================================================
#                    SALES FUNCTIONS
# ============================================================

def record_sale(product_id, quantity, selling_price):
    """
    Naya sale record karta hai AUR product ka stock automatically kam karta hai.
    Return: (success: bool, message: str)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Pehle current stock check karte hain
    cursor.execute("SELECT current_stock FROM products WHERE product_id = ?", (product_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return False, "Product nahi mila."

    current_stock = row[0]

    if quantity <= 0:
        conn.close()
        return False, "Quantity 0 se zyada honi chahiye."

    if quantity > current_stock:
        conn.close()
        return False, f"Insufficient stock! Sirf {current_stock} units available hain."

    total_amount = quantity * selling_price
    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sale insert karo
    cursor.execute("""
        INSERT INTO sales (product_id, quantity, selling_price, total_amount, sale_date)
        VALUES (?, ?, ?, ?, ?)
    """, (product_id, quantity, selling_price, total_amount, sale_date))

    # Stock kam karo (yeh dono steps ek hi transaction mein hain)
    new_stock = current_stock - quantity
    cursor.execute("UPDATE products SET current_stock = ? WHERE product_id = ?", (new_stock, product_id))

    conn.commit()
    conn.close()
    return True, "Sale successfully record ho gayi!"


def get_all_sales():
    """Saari sales history deta hai, product name ke saath (JOIN)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sales.sale_id, products.name, sales.quantity, sales.selling_price,
               sales.total_amount, sales.sale_date
        FROM sales
        JOIN products ON sales.product_id = products.product_id
        ORDER BY sales.sale_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_sales_for_prediction(product_id):
    """Ek product ki saari sales (date, quantity) — prediction ke liye."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sale_date, quantity FROM sales
        WHERE product_id = ?
        ORDER BY sale_date ASC
    """, (product_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_today_sales_total():
    """Aaj ki total sales amount."""
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COALESCE(SUM(total_amount), 0) FROM sales
        WHERE sale_date LIKE ?
    """, (f"{today}%",))
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_total_sales_amount():
    """Ab tak ki total sales (all time)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM sales")
    total = cursor.fetchone()[0]
    conn.close()
    return total
