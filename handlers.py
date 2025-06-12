from utils import *
from db import get_connection

def handle_message(data):
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone = msg["from"]
        text = msg.get("text", {}).get("body", "")

        intent = detect_intent(text)

        if intent == "catalog":
            send_product_list(phone)
        elif intent == "order":
            send_text(phone, "Please share your delivery address.")
        elif intent == "credit":
            send_credit(phone)
        elif intent == "history":
            send_order_history(phone)
        elif intent == "help":
            send_template(phone, "support_message")
        else:
            send_text(phone, "Type 'catalog', 'order', 'credit', or 'help'.")
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()

def send_credit(phone):
    uid = get_user_id_by_phone(phone)
    if uid:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT balance, wallet_points FROM credit_history WHERE user_id = %s", (uid,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        msg = f"Balance: ₹{row['balance']}, Points: {row['wallet_points']}" if row else "No credit data."
        send_text(phone, msg)
    else:
        send_text(phone, "User not found.")

def send_order_history(phone):
    uid = get_user_id_by_phone(phone)
    if uid:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT order_id, products, payment_status FROM order_history WHERE user_id = %s", (uid,))
        orders = cur.fetchall()
        cur.close()
        conn.close()
        msg = "\n".join([f"Order #{o['order_id']}: {o['products']} ({o['payment_status']})" for o in orders]) if orders else "No orders found."
        send_text(phone, msg)
    else:
        send_text(phone, "User not found.")
