import requests
import time

# Telegram Bot Token and Chat ID
BOT_TOKEN = "7710027411:AAEtCULzYhfrQS4lzHzV2-UA5BhLHIel8Zs"
CHAT_ID = "927311167"

# Function to send Telegram alert
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    return response.json()

# Function to get total number of Bitcoin nodes
def get_total_nodes():
    response = requests.get("https://bitnodes.io/api/v1/snapshots/latest/")
    if response.status_code == 200:
        data = response.json()
        total_nodes = data.get("total_nodes", 0)
        return total_nodes
    return None

# Main logic loop
previous_node_count = None

while True:
    current_node_count = get_total_nodes()
    if current_node_count is not None:
        if previous_node_count is not None:
            change = current_node_count - previous_node_count
            if abs(change) >= 50:  # Threshold: node count change 50+
                direction = "📈 Increase" if change > 0 else "📉 Decrease"
                message = f"🚨 Bitnodes Alert!\n\n{direction} in Bitcoin nodes: {change}\nTotal Nodes: {current_node_count}"
                send_telegram_alert(message)
        previous_node_count = current_node_count
    time.sleep(60)  # Check every 60 seconds
