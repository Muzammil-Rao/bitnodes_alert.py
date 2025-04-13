import requests
import time
import telebot

# === CONFIGURATION ===
BOT_TOKEN = '7710027411:AAEtCULzYhfrQS4lzHzV2-UA5BhLHIel8Zs'
CHAT_ID = '927311167'
CHECK_INTERVAL = 300  # 5 minutes
SIGNIFICANT_DROP = 100  # threshold for alert

bot = telebot.TeleBot(BOT_TOKEN)

# === GLOBAL STATE ===
last_node_count = None

# === BOT COMMAND: /status ===
@bot.message_handler(commands=['status'])
def send_status(message):
    try:
        data = requests.get("https://bitnodes.io/api/v1/snapshots/latest/").json()
        node_count = data['total_nodes']
        bot.reply_to(message, f"📊 Current Total Nodes: {node_count}\n⏱️ Time: {int(time.time())}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error fetching status:\n{e}")

# === ALERT LOOP ===
def check_bitnodes():
    global last_node_count
    while True:
        try:
            response = requests.get("https://bitnodes.io/api/v1/snapshots/latest/").json()
            current_nodes = response['total_nodes']

            if last_node_count is not None:
                change = current_nodes - last_node_count
                percent_change = (change / last_node_count) * 100

                if abs(change) >= SIGNIFICANT_DROP:
                    symbol = "📈 Increase" if change > 0 else "📉 Decrease"
                    alert = (
                        f"🚨 Bitnodes Alert!\n"
                        f"{symbol} in Bitcoin Nodes: {change} ({percent_change:.2f}%)\n"
                        f"🧠 Total Nodes: {current_nodes}\n"
                        f"⏰ Time: {int(time.time())}"
                    )
                    bot.send_message(CHAT_ID, alert)

            last_node_count = current_nodes
        except Exception as e:
            bot.send_message(CHAT_ID, f"⚠️ Error in node check:\n{e}")

        time.sleep(CHECK_INTERVAL)

# === RUN THE MONITOR IN BACKGROUND ===
import threading
monitor_thread = threading.Thread(target=check_bitnodes)
monitor_thread.daemon = True
monitor_thread.start()

print("🚀 Bot is running...")
bot.polling()

