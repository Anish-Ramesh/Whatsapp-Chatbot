import requests
from db import get_connection
from test_mode import IS_TEST_MODE

# Meta Configs
ACCESS_TOKEN = "your_access_token"
PHONE_ID = "your_phone_id"
CATALOG_ID = "your_catalog_id"
WABA_ID = "your_whatsapp_business_account_id"

def send_text(phone, msg):
    if IS_TEST_MODE:
        print(f"[TEST MODE] To: {phone} → {msg}")
        return

    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": msg}
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

def send_product_list(phone):
    retailer_ids = ["prod123", "prod456"]  # Hardcoded sample products
    if IS_TEST_MODE:
        print(f"[TEST MODE] Sending catalog to {phone}")
        return

    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "product_list",
            "body": {
                "text": "Here are our products"
            },
            "action": {
                "catalog_id": CATALOG_ID,
                "sections": [{
                    "title": "Available Products",
                    "product_items": [{"product_retailer_id": r} for r in retailer_ids]
                }]
            }
        }
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)
    sync_products(retailer_ids)

def send_template(phone, template_name):
    if IS_TEST_MODE:
        print(f"[TEST MODE] Sending template {template_name} to {phone}")
        return

    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en_US"}
        }
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

def create_template(name, body_text, category="TRANSACTIONAL"):
    if IS_TEST_MODE:
        print(f"[TEST MODE] Creating template '{name}': {body_text}")
        return

    url = f"https://graph.facebook.com/v19.0/{WABA_ID}/message_templates"
    payload = {
        "name": name,
        "category": category,
        "language": "en_US",
        "components": [
            {
                "type": "BODY",
                "text": body_text
            }
        ]
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())

def get_user_id_by_phone(phone):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM users WHERE phone_number = %s", (phone,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row['id'] if row else None

def sync_products(retailer_ids):
    conn = get_connection()
    cur = conn.cursor()
    for rid in retailer_ids:
        cur.execute("INSERT IGNORE INTO products (retailer_id, name, price) VALUES (%s, %s, %s)", (rid, rid, 0.0))
    conn.commit()
    cur.close()
    conn.close()

def detect_intent(text):
    text = text.lower()
    if "catalog" in text: return "catalog"
    elif "order" in text: return "order"
    elif "credit" in text: return "credit"
    elif "history" in text: return "history"
    elif "help" in text: return "help"
    else: return "unknown"
