from flask import Flask, request, jsonify
from Main_login import handle_signal
import os

app = Flask(__name__)

# ==============================
# HEALTH CHECK ROUTE (FIXES 404)
# ==============================
@app.route('/', methods=['GET'])
def home():
    return "Bot is running 🚀", 200


# ==============================
# WEBHOOK ROUTE
# ==============================
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
    except:
        data = request.data.decode("utf-8")

    print("\n📩 Raw data received:", data)

    # Normalize signal
    if isinstance(data, dict):
        signal = data.get("signal", "")
    else:
        signal = data

    # Clean signal
    signal = str(signal).upper().strip()

    if "BUY" in signal:
        signal = "BUY"
    elif "SELL" in signal:
        signal = "SELL"
    else:
        signal = None

    print("🚀 Clean Signal:", signal)

    if signal:
        handle_signal(signal)
    else:
        print("⚠️ Unknown signal")

    return jsonify({"status": "ok"}), 200


# ==============================
# RUN LOCAL (NOT USED IN RENDER)
# ==============================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
