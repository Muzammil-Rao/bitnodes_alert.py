import requests
import time

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
            print("Failed to send message:", response.text)
    except Exception as e:
        print("Error sending message:", e)

# === MAIN LOGIC ===
def check_bitnodes():
    try:
        response = requests.get(BITNODES_API)
        data = response.json()
        total_nodes = data.get("total_nodes", "N/A")
        timestamp = data.get("timestamp", "Unknown")
        msg = f"🔔 Bitnodes Snapshot:\n🧠 Total Nodes: {total_nodes}\n⏰ Time: {timestamp}"
        print(msg)
        send_message(msg)
    except Exception as e:
        print("Error fetching bitnodes data:", e)

# === STARTUP MESSAGE ===
print("🚀 Bitnodes Alert Bot is running...")
send_message("🚀 Bitnodes Alert Bot started successfully!")

# === LOOP FOREVER ===
while True:
    check_bitnodes()
    time.sleep(300)  # 5 minutes
