import os
from dotenv import load_dotenv
import requests

load_dotenv()

CATALOG_ID = os.getenv("CATALOG_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GRAPH_API_URL = "https://graph.facebook.com/v19.0"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def list_products():
    url = f"{GRAPH_API_URL}/{CATALOG_ID}/products?access_token={ACCESS_TOKEN}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def get_product(product_id):
    url = f"{GRAPH_API_URL}/{product_id}?access_token={ACCESS_TOKEN}"
    resp = requests.get(url)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()

def send_product_message(phone, retailer_id):
    url = f"{GRAPH_API_URL}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "action",
        "action": {
            "catalog_id": CATALOG_ID,
            "product_retailer_id": retailer_id
        }
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()

def send_multi_product_message(phone, retailer_ids, section_title="Products"):
    url = f"{GRAPH_API_URL}/{PHONE_NUMBER_ID}/messages"
    section = {
        "title": section_title,
        "product_items": [{"product_retailer_id": rid} for rid in retailer_ids]
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "product_list",
            "header": {"type": "text", "text": "Check out our products!"},
            "body": {"text": "Browse and shop directly"},
            "footer": {"text": "Powered by WhatsApp"},
            "action": {
                "catalog_id": CATALOG_ID,
                "sections": [section]
            }
        }
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()