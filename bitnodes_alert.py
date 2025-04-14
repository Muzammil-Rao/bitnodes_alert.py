import os
import requests
import logging
import matplotlib.pyplot as plt
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, Dispatcher
from io import BytesIO
from flask import Flask, request
from datetime import datetime

# --- Config ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = 'https://bitnodes.io/api/v1/snapshots/latest/'

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

previous_count = None
history = []

# --- Chart Function ---
def generate_chart():
    times = [x[0] for x in history]
    values = [x[1] for x in history]
    plt.figure(figsize=(6, 3))
    plt.plot(times, values, marker='o', color='blue')
    plt.title('Bitnodes Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

# --- Bot Commands ---
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="👋 Bitnodes Alert Bot is live via Webhook!")

def status(update, context):
    if previous_count:
        chart = generate_chart()
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"📊 Current node count: {previous_count}")
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Data not available yet.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("status", status))

# --- Fetch Logic ---
def fetch_bitnodes_data():
    global previous_count
    try:
        res = requests.get(API_URL)
        if res.status_code == 200:
            data = res.json()
            current = data['total_nodes']
            now = datetime.now().strftime("%H:%M")
            history.append((now, current))
            if len(history) > 12:
                history.pop(0)

            if previous_count:
                diff = current - previous_count
                perc = (diff / previous_count) * 100
                if abs(perc) >= 0.5:
                    trend = "📈 Bullish" if diff > 0 else "📉 Bearish"
                    msg = f"🔔 *Bitnodes Alert*\nNodes: {previous_count} → {current}\nChange: {diff} ({perc:.2f}%)\nSignal: {trend}"
                    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            previous_count = current
    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"❌ Error fetching data: {e}")

# --- Webhook ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def index():
    return "Bitnodes Webhook Bot Active!", 200

# --- Start ---
if __name__ == "__main__":
    import threading
    import time

    def periodic():
        while True:
            fetch_bitnodes_data()
            time.sleep(1800)  # 30 min

    threading.Thread(target=periodic).start()
    PORT = int(os.environ.get("PORT", 5000))
    
    # 👇👇👇 Webhook URL updated here
    bot.set_webhook("https://illustrious-renewal.up.railway.app/7710027411:AAEtCULzYhfrQS4lzHzV2-UA5BhLHIel8Zs")
    
    app.run(host="0.0.0.0", port=PORT)
