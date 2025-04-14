import requests
from bs4 import BeautifulSoup
import time
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater
from datetime import datetime

# ========== CONFIG ==========
BOT_TOKEN = "7710027411:AAEtCULzYhfrQS4lzHzV2-UA5BhLHIel8Zs"
CHAT_ID = "927311167"  # Optional: For auto alerts
CHECK_INTERVAL = 600  # in seconds (10 min)
SIGNAL_THRESHOLD = 10  # node count change to trigger signal
# ============================

previous_node_count = None

def fetch_bitnodes_count():
    try:
        response = requests.get("https://bitnodes.io/")
        soup = BeautifulSoup(response.text, "html.parser")
        node_count_tag = soup.find("h3", string=lambda text: "reachable nodes" in text.lower())
        if node_count_tag:
            count = int("".join(filter(str.isdigit, node_count_tag.text)))
            return count
        else:
            return None
    except Exception as e:
        print(f"Scraping Error: {e}")
        return None

def get_signal(change):
    if change >= SIGNAL_THRESHOLD:
        return "Bullish 📈"
    elif change <= -SIGNAL_THRESHOLD:
        return "Bearish 📉"
    else:
        return "Neutral 🔍"

def send_alert(bot, current_count, change, signal):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    message = f"""🚨 Bitnodes Alert!

{("📈 Increase" if change > 0 else "📉 Decrease")} in Bitcoin nodes: {change}
🧠 Total Nodes: {current_count}
⏰ Time: {now}
📊 Signal: {signal}
"""
    bot.send_message(chat_id=CHAT_ID, text=message)

def start_tracking():
    global previous_node_count
    bot = Bot(token=BOT_TOKEN)

    while True:
        current_count = fetch_bitnodes_count()
        if current_count is None:
            bot.send_message(chat_id=CHAT_ID, text="⚠️ Failed to fetch Bitnodes data from website.")
        else:
            if previous_node_count is None:
                # First snapshot
                previous_node_count = current_count
                now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                bot.send_message(chat_id=CHAT_ID, text=f"""🚨 Bitnodes Alert!
🔢 First snapshot - tracking started
🧠 Total Nodes: {current_count}
⏰ Time: {now}
📊 Signal: N/A
""")
            else:
                change = current_count - previous_node_count
                signal = get_signal(change)
                send_alert(bot, current_count, change, signal)
                previous_node_count = current_count
        time.sleep(CHECK_INTERVAL)

# ===== /status command handler =====
def status_command(update: Update, context):
    current_count = fetch_bitnodes_count()
    if current_count is not None:
        update.message.reply_text(f"📊 Current total Bitcoin nodes: {current_count}")
    else:
        update.message.reply_text("⚠️ Failed to fetch current data.")

def setup_command_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("status", status_command))
    updater.start_polling()
    return updater

if __name__ == "__main__":
    from threading import Thread
    print("🚀 Bitnodes Alert Bot (FREE version using scraping) Started!")
    # Run command bot in parallel
    command_thread = Thread(target=setup_command_bot)
    command_thread.start()

    # Start the main tracker
    start_tracking()
