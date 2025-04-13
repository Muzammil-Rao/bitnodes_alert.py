import time
import requests
import telegram
from telegram.ext import Updater, CommandHandler

TOKEN = "7710027411:AAEtCULzYhfrQS4lzHzV2-UA5BhLHIel8Zs"
CHAT_ID = "927311167"

bot = telegram.Bot(token=TOKEN)
previous_nodes = None
SIGNIFICANT_CHANGE = 200  # +/- change to trigger alert

def get_node_count():
    try:
        response = requests.get("https://bitnodes.io/api/v1/snapshots/latest/")
        return response.json()["total_nodes"]
    except Exception as e:
        return None

def send_alert(current, previous):
    change = current - previous
    emoji = "📉" if change < 0 else "📈"
    msg = f"""🚨 Bitnodes Alert!
{emoji} Change in Bitcoin Nodes: {change}
🧠 Total Nodes: {current}
⏰ Time: {int(time.time())}"""
    bot.send_message(chat_id=CHAT_ID, text=msg)

def status(update, context):
    current = get_node_count()
    update.message.reply_text(f"🔍 Current Bitcoin Nodes: {current}")

def main_loop():
    global previous_nodes
    while True:
        current_nodes = get_node_count()
        if current_nodes is not None:
            if previous_nodes is not None:
                if abs(current_nodes - previous_nodes) >= SIGNIFICANT_CHANGE:
                    send_alert(current_nodes, previous_nodes)
            previous_nodes = current_nodes
        time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("status", status))
    updater.start_polling()

    main_loop()
