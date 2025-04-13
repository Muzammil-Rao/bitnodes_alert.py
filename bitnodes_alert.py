import time
import requests
import datetime
import telegram

TOKEN = "7710027411:AAEtCULzYhfrQS4lzHzV2-UA5BhLHIel8Zs"
CHAT_ID = "927311167"

bot = telegram.Bot(token=TOKEN)
url = "https://bitnodes.io/api/v1/snapshots/latest/"

def get_node_count():
    response = requests.get(url)
    data = response.json()
    return data["total_nodes"]

previous_nodes = get_node_count()

# Initial success message
await bot.send_message(chat_id=CHAT_ID, text=f"""🚀 Bitnodes Alert Bot started successfully!
🔔 Bitnodes Snapshot:
🧠 Total Nodes: {previous_nodes}
⏰ Time: {int(time.time())}
""")

while True:
    time.sleep(300)  # 5 minutes

    current_nodes = get_node_count()
    change = current_nodes - previous_nodes

    # Alert only if there's a noticeable change (e.g., 100+)
    if abs(change) >= 100:
        direction = "📉 Decrease" if change < 0 else "📈 Increase"
        msg = f"""⚠️ Bitnodes Alert!

{direction} in Bitcoin nodes: {change}
Total Nodes: {current_nodes}
⏰ Time: {int(time.time())}
"""
        bot.send_message(chat_id=CHAT_ID, text=msg)
        previous_nodes = current_nodes
    else:
        print(f"No major change. Current: {current_nodes}, Previous: {previous_nodes}")
