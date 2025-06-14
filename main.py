import time
import threading
import requests
import telebot
from flask import Flask
import os

# --- Налаштування ---
BOT_TOKEN = '8123961931:AAF_NrjyHnEqwb4FzTywORBWwyi2FKp_MRs'
CHANNEL = '@b_shelter'

ALERT_STICKER = 'CAACAgIAAxkBAAEOrudoSZ8PeLC5ug8n6Zss5a_cdHwvwwACrXEAAtMcQUqVXKBdnTw7aDYE'
CLEAR_STICKER = 'CAACAgIAAxkBAAEOruloSZ8x1sfzXi5mwJVfAvhSAAGh_z0AAqdlAAIGPkBKRnqQyR78Ajg2BA'

API_URL = 'https://api.alerts.in.ua/v1/alerts/active.json'
API_TOKEN = '43f24461d276238f96128d073eb1562692e230a1ab2203'

bot = telebot.TeleBot(BOT_TOKEN)

# --- Flask сервер ---
app = Flask(__name__)

@app.route('/')
def home():
    return 'Бот працює ✅'

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- Перевірка тривоги ---
def check_alert(data):
    alerts = data.get('alerts', [])
    for alert in alerts:
        location = alert.get('location_title', '').lower()
        if 'одеська' in location:
            return True
    return False

def bot_loop():
    print("Запуск циклу перевірки тривоги")
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'User-Agent': 'Mozilla/5.0',
    }

    last_alert = False

    # Початкова перевірка
    try:
        r = requests.get(API_URL, headers=headers, timeout=5)
        print(f"HTTP статус початкової перевірки: {r.status_code}")
        r.raise_for_status()
        data = r.json()
        print(f"Отримано {len(data.get('alerts', []))} тривог при старті")
        last_alert = check_alert(data)
        print(f"Стартове значення тривоги: {last_alert}")
    except Exception as e:
        print(f"Помилка при стартовій перевірці: {e}")

    while True:
        try:
            r = requests.get(API_URL, headers=headers, timeout=5)
            print(f"HTTP статус запиту: {r.status_code}")
            r.raise_for_status()
            data = r.json()
            alert_now = check_alert(data)
            print(f"Тривога зараз: {alert_now}")

            if alert_now and not last_alert:
                print("⚠️ Нова тривога! Відправляємо стікер.")
                try:
                    bot.send_sticker(CHANNEL, ALERT_STICKER)
                except Exception as e:
                    print(f"Помилка при відправці стікера тривоги: {e}")
                last_alert = True

            elif not alert_now and last_alert:
                print("✅ Відбій тривоги! Відправляємо стікер.")
                try:
                    bot.send_sticker(CHANNEL, CLEAR_STICKER)
                except Exception as e:
                    print(f"Помилка при відправці стікера відбою: {e}")
                last_alert = False

        except Exception as e:
            print(f"Помилка у циклі перевірки: {e}")

        time.sleep(15)

# --- Запуск ---
if __name__ == '__main__':
    print("Запуск програми")
    threading.Thread(target=run_flask).start()
    print("Запуск bot_loop")
    bot_loop()
