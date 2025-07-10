# --- FILE: app.py ---

from flask import Flask, request
from handlers import handle_message
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")  

@app.route('/', methods=['GET'])
def index():
    return "WhatsApp Bot is running.", 200

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully.")
        return challenge, 200
    else:
        return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("[WEBHOOK] POST received")
        data = request.get_json(force=True, silent=True)
        if not data:
            print("[ERROR] No JSON payload received!")
            return "No JSON payload", 400
        handle_message(data)
        return "OK", 200
    except Exception as e:
        print(f"[ERROR] Exception in webhook: {e}")
        return f"Webhook error: {e}", 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
