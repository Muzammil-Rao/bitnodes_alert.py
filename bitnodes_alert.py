import requests
import time
import logging
import matplotlib.pyplot as plt
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater
from io import BytesIO
from datetime import datetime

# --- Config ---
BOT_TOKEN = '7710027411:AAEtCULzYhfrQS4lzHzV2-UA5BhLHIel8Zs'
CHAT_ID = '927311167'
API_URL = 'https://bitnodes.io/api/v1/snapshots/latest/'
CHECK_INTERVAL = 1800  # 30 mins

# --- Setup ---
bot = Bot(token=BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(level=logging.INFO)

previous_count = None
history = []

# --- Chart ---
def generate_chart():
    times = [x[0] for x in history]
    values = [x[1] for x in history]

    plt.figure(figsize=(6, 3))
    plt.plot(times, values, marker='o', color='blue')
    plt.title('Bitnodes Count')
    plt.xlabel('Time')
    plt.ylabel('Nodes')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer

# --- Commands ---
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="👋 Bitnodes Alert Bot is running!")

def status(update, context):
    if previous_count is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"📊 Current node count: {previous_count}")
        chart = generate_chart()
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Data not available yet. Please wait.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("status", status))

# --- Main Logic ---
def fetch_bitnodes_data():
    global previous_count
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            current_count = data['total_nodes']
            now = datetime.now().strftime('%H:%M')

            history.append((now, current_count))
            if len(history) > 12:
                history.pop(0)

            if previous_count is not None:
                change = current_count - previous_count
                percentage = (change / previous_count) * 100

                if abs(percentage) >= 0.5:  # Alert threshold
                    signal = "📈 Bullish" if change > 0 else "📉 Bearish"
                    message = (
                        f"🔔 *Bitnodes Alert*\n"
                        f"Nodes: {previous_count} → {current_count}\n"
                        f"Change: {change} ({percentage:.2f}%)\n"
                        f"Signal: {signal}"
                    )
                    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
            previous_count = current_count

        else:
            logging.warning("API Error: %s", response.text)
            bot.send_message(chat_id=CHAT_ID, text="⚠️ Failed to fetch Bitnodes data from API.")
    except Exception as e:
        logging.error("Error: %s", e)
        bot.send_message(chat_id=CHAT_ID, text=f"❌ Exception occurred: {e}")

# --- Loop ---
def run_bot():
    updater.start_polling()
    while True:
        fetch_bitnodes_data()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_bot()
