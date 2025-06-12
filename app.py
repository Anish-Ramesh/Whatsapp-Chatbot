from flask import Flask, request, jsonify
from handlers import handle_message

app = Flask(__name__)
VERIFY_TOKEN = "your_verify_token"

@app.route("/")
def home():
    return "WhatsApp Bot is running."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Unauthorized", 403
    if request.method == "POST":
        data = request.get_json()
        handle_message(data)
        return "OK", 200

# Local test endpoint v2
@app.route("/local_test", methods=["POST"])
def local_test():
    data = request.get_json()
    handle_message(data)
    return jsonify({"status": "message processed locally"}), 200

if __name__ == "__main__":
    app.run(debug=True)
