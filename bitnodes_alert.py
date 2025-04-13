import requests
import time
import datetime

# === CONFIG ===
BOT_TOKEN = "7710027411:AAEtCULzYhfrQS4lzHzV2-UA5BhLHIel8Zs"
CHAT_ID = "927311167"
BITNODES_API = "https://bitnodes.io/api/v1/snapshots/latest/"

previous_nodes = None  # For tracking node change

# === SEND TELEGRAM ALERT ===
def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print("❌ Failed to send message:", response.text)
    except Exception as e:
        print("⚠️ Error sending message:", e)

# === CHECK BITNODES ===
def check_bitnodes():
    global previous_nodes

    try:
        response = requests.get(BITNODES_API)
        if response.status_code == 200:
            data = response.json()
            total_nodes = data.get("total_nodes")
            timestamp = data.get("timestamp")

            if total_nodes is None or timestamp is None:
                raise ValueError("Invalid data from API")

            readable_time = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')

            if previous_nodes is not None:
                diff = total_nodes - previous_nodes
                if diff > 0:
                    trend = f"📈 Increase in Bitcoin nodes: +{diff}"
                    signal = "📊 Signal: Bullish 🔼"
                elif diff < 0:
                    trend = f"📉 Decrease in Bitcoin nodes: {diff}"
                    signal = "📊 Signal: Bearish 🔽"
                else:
                    trend = "➖ No change in Bitcoin nodes"
                    signal = "📊 Signal: Neutral ⏸️"
            else:
                trend = "ℹ️ First snapshot - tracking started"
                signal = "📊 Signal: N/A"

            previous_nodes = total_nodes

            msg = f"""🚨 Bitnodes Alert!

{trend}
🧠 Total Nodes: {total_nodes}
⏰ Time: {readable_time}
{signal}"""

            print(msg)
            send_message(msg)
        else:
            print("❌ Failed to fetch data from Bitnodes:", response.text)
            send_message("⚠️ Failed to fetch Bitnodes data from API.")
    except Exception as e:
        print("⚠️ Exception occurred while fetching data:", e)
        send_message("⚠️ Exception occurred while fetching Bitnodes data.")

# === STARTUP ===
print("🚀 Bitnodes Alert Bot is running...")
send_message("🚀 Bitnodes Alert Bot with Signal Detection started!")

# === LOOP ===
while True:
    check_bitnodes()
    time.sleep(300)  # Run every 5 minutes
