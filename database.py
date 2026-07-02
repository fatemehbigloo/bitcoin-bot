import sqlite3
import datetime

# اتصال به دیتابیس
DB_NAME = 'btc_prices.db'

def init_db():
    """ایجاد جداول دیتابیس در صورت عدم وجود"""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = conn.cursor()

        # ایجاد جدول قیمت‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                price REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ایجاد جدول کاربران
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT UNIQUE NOT NULL,
                registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        print("دیتابیس و جداول با موفقیت ایجاد یا بررسی شدند.")
    except sqlite3.Error as e:
        print(f"خطا در ایجاد دیتابیس: {e}")
    finally:
        if conn:
            conn.close()

def save_price(price):
    """ذخیره قیمت جدید در جدول prices"""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO prices (price, timestamp) VALUES (?, ?)", (price, datetime.datetime.now()))
        conn.commit()
        # print(f"قیمت {price} با موفقیت ذخیره شد.")
    except sqlite3.Error as e:
        print(f"خطا در ذخیره قیمت: {e}")
    finally:
        if conn:
            conn.close()

def get_last_price():
    """دریافت آخرین قیمت ثبت شده از جدول prices"""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM prices ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except sqlite3.Error as e:
        print(f"خطا در دریافت آخرین قیمت: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_prices():
    """دریافت تمام قیمت‌های ثبت شده از جدول prices"""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM prices ORDER BY timestamp ASC")
        results = cursor.fetchall()
        return [row[0] for row in results]
    except sqlite3.Error as e:
        print(f"خطا در دریافت تمام قیمت‌ها: {e}")
        return []
    finally:
        if conn:
            conn.close()

def save_chat_id(chat_id):
    """ذخیره chat_id کاربر در جدول users با جلوگیری از تکرار"""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = conn.cursor()
        # INSERT OR IGNORE برای جلوگیری از خطا در صورت وجود chat_id
        cursor.execute("INSERT OR IGNORE INTO users (chat_id, registered_at) VALUES (?, ?)", (chat_id, datetime.datetime.now()))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Chat ID {chat_id} با موفقیت ذخیره شد.")
        else:
            print(f"Chat ID {chat_id} از قبل در دیتابیس وجود دارد.")
    except sqlite3.Error as e:
        print(f"خطا در ذخیره chat_id: {e}")
    finally:
        if conn:
            conn.close()

def get_all_chat_ids():
    """دریافت لیست تمام chat_id های ثبت شده از جدول users"""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM users")
        results = cursor.fetchall()
        # برگرداندن لیست chat_id ها
        return [row[0] for row in results]
    except sqlite3.Error as e:
        print(f"خطا در دریافت تمام chat_id ها: {e}")
        return []
    finally:
        if conn:
            conn.close()

def is_user_registered(chat_id):
    """بررسی اینکه آیا chat_id خاصی در جدول users وجود دارد یا خیر"""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE chat_id = ?", (chat_id,))
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        print(f"خطا در بررسی ثبت نام کاربر: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- اجرای اولیه برای اطمینان از وجود دیتابیس و جداول ---
# init_db() # این تابع در bit.py صدا زده می‌شود، نیازی به تکرار اینجا نیست.
