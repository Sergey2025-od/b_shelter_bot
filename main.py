import os
import time
import threading
import requests
import telebot
from flask import Flask

# === Налаштування ===
BOT_TOKEN = '8123961931:AAF_NrjyHnEqwb4FzTywORBWwyi2FKp_MRs'
CHANNEL = '@b_shelter'

API_URL = 'https://api.alerts.in.ua/v1/alerts/active.json'
API_TOKEN = '43f24461d276238f96128d073eb1562692e230a1ab2203'

ALERT_STICKER = 'CAACAgIAAxkBAAEOrudoSZ8PeLC5ug8n6Zss5a_cdHwvwwACrXEAAtMcQUqVXKBdnTw7aDYE'
CLEAR_STICKER = 'CAACAgIAAxkBAAEOruloSZ8x1sfzXi5mwJVfAvhSAAGh_z0AAqdlAAIGPkBKRnqQyR78Ajg2BA'

# === Ініціалізація ===
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
last_alert = None  # Глобальна змінна стану

@app.route('/')
def home():
    return 'Бот працює ✅'

def check_alert(data):
    alerts = data.get('alerts', [])
    for alert in alerts:
        location = alert.get('location_title', '').lower()
        if 'одеська' in location:
            return True
    return False

def alert_monitor():
    global last_alert
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'User-Agent': 'Mozilla/5.0',
    }

    while True:
        try:
            response = requests.get(API_URL, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            is_alert_now = check_alert(data)

            if is_alert_now and last_alert is not True:
                bot.send_sticker(CHANNEL, ALERT_STICKER)
                last_alert = True
                print(">>> ТРИВОГА! Стікер надіслано.")

            elif not is_alert_now and last_alert is not False:
                bot.send_sticker(CHANNEL, CLEAR_STICKER)
                last_alert = False
                print(">>> ВІДБІЙ! Стікер надіслано.")

        except Exception as e:
            print(f"❌ Помилка: {e}")

        time.sleep(10)

def run_monitor():
    thread = threading.Thread(target=alert_monitor)
    thread.daemon = True
    thread.start()

# === Запуск ===
if __name__ == '__main__':
    print(">>> Запуск бота та сервера Flask")
    run_monitor()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
