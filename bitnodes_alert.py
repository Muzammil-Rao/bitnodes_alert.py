import requests
import time
import datetime

# === CONFIG ===
BOT_TOKEN = "7710027411:AAEtCULzYhfrQS4lzHzV2-UA5BhLHIel8Zs"
CHAT_ID = "927311167"
BITNODES_API = "https://bitnodes.io/api/v1/snapshots/latest/"

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

# === CHECK BITNODES STATUS ===
def check_bitnodes():
    try:
        response = requests.get(BITNODES_API)
        if response.status_code == 200:
            data = response.json()
            total_nodes = data.get("total_nodes")
            timestamp = data.get("timestamp")

            if total_nodes is None or timestamp is None:
                raise ValueError("Invalid data from API")

            # Convert timestamp to readable UTC time
            readable_time = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')

            # Final message
            msg = f"🔔 Bitnodes Snapshot:\n🧠 Total Nodes: {total_nodes}\n⏰ Time: {readable_time}"
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
send_message("🚀 Bitnodes Alert Bot started successfully!")

# === LOOP FOREVER ===
while True:
    check_bitnodes()
    time.sleep(300)  # 5 minutes delay
