# --- FILE: db.py ---
import hashlib
import mysql.connector
import json as _json
import os
from dotenv import load_dotenv
import logging
import datetime 

load_dotenv()

def get_connection():
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

def ensure_user_exists(phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT IGNORE INTO users (phone_number) VALUES (%s)", (phone,))
    conn.commit()
    cur.close()
    conn.close()

def get_user_id(phone):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE phone_number = %s", (phone,))
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        print("DB Error in get_user_id:", e)
        return None
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def update_user_language(phone, lang_code):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET language = %s WHERE phone_number = %s", (lang_code, phone))
    conn.commit()
    cur.close()
    conn.close()

def get_user_language(phone):
    conn = get_connection()
    cur = conn.cursor()
    phone = phone[1:]
    cur.execute("SELECT language FROM users WHERE phone_number = %s", (phone,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result and result[0]:
        return result[0]
    return None

def update_user_address(phone, address):
    conn = get_connection()
    cur = conn.cursor()
    # Ensure user exists
    cur.execute("SELECT id FROM users WHERE phone_number = %s", (phone,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (phone_number) VALUES (%s)", (phone,))

    # Update address
    cur.execute("UPDATE users SET address = %s WHERE phone_number = %s", (address, phone))

    conn.commit()
    cur.close()
    conn.close()


# --- Persistent user_context ---
def get_user_context(phone):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT context_json FROM user_context WHERE phone = %s", (phone,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row and row[0]:
            return _json.loads(row[0])
        return None
    except Exception as e:
        print("DB Error in get_user_context:", e)
        return None

def set_user_context(phone, context_dict):
    try:
        conn = get_connection()
        cur = conn.cursor()
        context_json = _json.dumps(context_dict)
        cur.execute("REPLACE INTO user_context (phone, context_json) VALUES (%s, %s)", (phone, context_json))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB Error in set_user_context:", e)

def clear_user_context(phone):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM user_context WHERE phone = %s", (phone,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB Error in clear_user_context:", e)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Seller Session Management ---
def login_seller_session(phone):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("REPLACE INTO seller_sessions (phone_number, login_time) VALUES (%s, NOW())", (phone,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB Error in login_seller_session:", e)

def logout_seller_session(phone):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM seller_sessions WHERE phone_number = %s", (phone,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB Error in logout_seller_session:", e)

def is_seller_session(phone):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT phone_number FROM seller_sessions WHERE phone_number = %s", (phone,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return bool(result)
    except Exception as e:
        print("DB Error in is_seller_session:", e)
        return False

# --- Seller Management ---
def register_seller(phone, password="SELLERPASS123"):
    try:
        conn = get_connection()
        cur = conn.cursor()
        password_hash = hash_password(password)
        cur.execute("INSERT INTO sellers (phone_number, password_hash, created_at) VALUES (%s, %s, NOW()) ON DUPLICATE KEY UPDATE password_hash=%s", (phone, password_hash, password_hash))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB Error in register_seller:", e)

def get_all_user_phones():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT user_phone FROM admin_alerts")
    result = cur.fetchall()
    return [row[0] for row in result] if result else []

def check_seller_password(phone, password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM sellers WHERE phone_number = %s", (phone,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return False
        return row[0] == hash_password(password)
    except Exception as e:
        print("DB Error in check_seller_password:", e)
        return False

def update_seller_password(phone, new_password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        password_hash = hash_password(new_password)
        cur.execute("UPDATE sellers SET password_hash = %s WHERE phone_number = %s", (password_hash, phone))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB Error in update_seller_password:", e)

def is_seller(phone):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM sellers WHERE phone_number = %s", (phone,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return bool(result)
    except Exception as e:
        print("DB Error in is_seller:", e)
        return False

def get_all_seller_phones():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT phone_number FROM sellers")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [row[0] for row in rows]
    except Exception as e:
        print("DB Error in get_all_seller_phones:", e)
        return []

# --- Admin Alerts ---
def store_admin_alert(alert_type, message, user_phone):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO admin_alerts (alert_type, message, user_phone) VALUES (%s, %s, %s)", (alert_type, message, user_phone))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB Error in store_admin_alert:", e)
        
def get_admin_alerts(phone, resolved=False):
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        r = 0
        cur.execute(
                    "SELECT * FROM admin_alerts WHERE resolved = %s AND user_phone = %s ORDER BY timestamp DESC",
                    (r, phone)
                )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print("DB Error in get_admin_alerts:", e)
        return []
    
def resolve_admin_alert(alert_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE admin_alerts SET resolved = 1 WHERE id = %s", (alert_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB Error in resolve_admin_alert:", e)

def get_alert_by_id(alert_id):
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM admin_alerts WHERE id = %s", (alert_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except Exception as e:
        print("DB Error in get_alert_by_id:", e)
        return None

def get_user_credit_history(user_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM credit_history WHERE user_id = %s", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# --- DB Connection Checker ---
def check_db_connection():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()  # fetch the result to clear the result set
        print("Database connection: SUCCESS")
        return True
    except Exception as e:
        print(f"Database connection: FAILED ({e})")
        return False

def get_user_orders(user_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_pending_bill(user_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM monthly_bills WHERE user_id = %s AND status = 'pending' ORDER BY bill_month DESC LIMIT 1", (user_id,))
    bill = cur.fetchone()
    cur.close()
    conn.close()
    return bill

def get_pending_bills_for_display(user_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM monthly_bills WHERE user_id = %s AND status = 'pending' ORDER BY bill_month ASC", (user_id,))
    bills = cur.fetchall()
    cur.close()
    conn.close()
    return bills

import datetime
from dateutil.relativedelta import relativedelta  # Make sure python-dateutil is installed

def carry_over_bill(bill_id):
    conn = get_connection()
    cur = conn.cursor()

    # Get current due_date
    cur.execute("SELECT due_date FROM monthly_bills WHERE id = %s", (bill_id,))
    result = cur.fetchone()
    if not result:
        cur.close()
        conn.close()
        raise ValueError("Bill ID not found.")

    current_due_date = result[0]
    new_due_date = current_due_date + relativedelta(months=1)

    # Update status and due_date
    cur.execute("""
        UPDATE monthly_bills 
        SET status = 'carried_over', due_date = %s 
        WHERE id = %s
    """, (new_due_date, bill_id))

    conn.commit()
    cur.close()
    conn.close()


def create_bill_for_order(user_id, order_id, total_amount,delivery_status):
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.date.today()
    bill_month = today.replace(day=1)
    next_month = bill_month.replace(day=28) + datetime.timedelta(days=4)
    due_date = next_month - datetime.timedelta(days=next_month.day)
    cur.execute("INSERT INTO monthly_bills (user_id, order_id, bill_month, total_amount, pending_amount, status, due_date) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user_id, order_id, bill_month, total_amount, total_amount, delivery_status, due_date))
    conn.commit()
    cur.close()
    conn.close()