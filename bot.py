import pandas as pd
import requests
import time

# === Telegram Bot Token ===
TOKEN = "8485070607:AAEo3OupUbB34E6POtfFhC1nBIGzcfBq1h0"  # Replace with your bot token
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# === Load CSV ===
csv_file = r"C:\DLB\routes.csv"  # Replace with your CSV file path
df = pd.read_csv(csv_file)
df['route'] = df['route'].str.upper()

# Optional: map route names to chat IDs (if you want specific chats)
# In this version, we reply to the chat that sent the message
route_chat_map = {route.upper(): True for route in df['route'].unique()}

# Track last update to avoid duplicates
offset = None

print("🤖 Bot started. Listening for messages...")

while True:
    try:
        url = f"{BASE_URL}/getUpdates?timeout=100"
        if offset:
            url += f"&offset={offset + 1}"
        updates = requests.get(url).json()

        for update in updates.get("result", []):
            offset = update["update_id"]

            msg = update.get("message")
            if not msg or "text" not in msg:
                continue

            text = msg["text"].strip().upper()
            chat_id = msg["chat"]["id"]

            # Check if text matches a route
            if text in route_chat_map:
                route_rows = df[df['route'] == text]

                if route_rows.empty:
                    response_text = f"❌ No data found for route '{text}'"
                else:
                    response_text = f"🗺️ Route List for {text}:\n"
                    for idx, row in enumerate(route_rows.itertuples(), start=1):
                        contact = row.contact if pd.notna(row.contact) else "N/A"
                        response_text += f"{idx}. {row.name} | Location: {row.location} | Contact: {contact}\n"

                # Send message back to the chat
                requests.post(f"{BASE_URL}/sendMessage", data={"chat_id": chat_id, "text": response_text})

    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(5)  # wait a bit before retrying
