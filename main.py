import time
import threading
import requests
import telebot
from flask import Flask
import os

# === Налаштування ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL")  # наприклад: '@b_shelter'

API_TOKEN = os.getenv("API_TOKEN")
API_URL = 'https://api.alerts.in.ua/v1/alerts/active.json'

ALERT_STICKER = 'CAACAgIAAxkBAAEOrudoSZ8PeLC5ug8n6Zss5a_cdHwvwwACrXEAAtMcQUqVXKBdnTw7aDYE'
CLEAR_STICKER = 'CAACAgIAAxkBAAEOruloSZ8x1sfzXi5mwJVfAvhSAAGh_z0AAqdlAAIGPkBKRnqQyR78Ajg2BA'

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return 'Бот працює ✅'

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def check_alert(data):
    alerts = data.get('alerts', [])
    for alert in alerts:
        location = alert.get('location_title', '').lower()
        if 'одеська' in location:
            return True
    return False

def bot_loop():
    print(">>> bot_loop стартує")
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'User-Agent': 'Mozilla/5.0'
    }

    last_alert = None

    while True:
        print(">>> tick ...")
        try:
            r = requests.get(API_URL, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            is_alert_now = check_alert(data)
            print(f">>> Тривога зараз: {is_alert_now}")

            if is_alert_now and last_alert is not True:
                print("⚠️ ТРИВОГА! Відправляємо стікер.")
                bot.send_sticker(CHANNEL, ALERT_STICKER)
                last_alert = True

            elif not is_alert_now and last_alert is not False:
                print("✅ ВІДБІЙ! Відправляємо стікер.")
                bot.send_sticker(CHANNEL, CLEAR_STICKER)
                last_alert = False

        except Exception as e:
            print(f"❌ Помилка: {e}")

        time.sleep(5)

if __name__ == '__main__':
    print("=== Старт основного процесу ===")
    threading.Thread(target=run_flask, daemon=True).start()
    bot_loop()
