import time
import threading
import requests
import telebot
from flask import Flask
import os

# --- Налаштування ---
BOT_TOKEN = '8123961931:AAF_NrjyHnEqwb4FzTywORBWwyi2FKp_MRs'  # Замінити на свій токен
CHANNEL = '@b_shelter'  # Канал або чат

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
    print(">>> Запуск циклу перевірки тривог")
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'User-Agent': 'Mozilla/5.0',
    }

    last_alert = None
    first_check = True

    while True:
        print(">>> tick ...")
        try:
            r = requests.get(API_URL, headers=headers, timeout=5)
            r.raise_for_status()
            data = r.json()
            is_alert_now = check_alert(data)
            print(f">>> Тривога зараз: {is_alert_now}")

            if first_check:
                print("👀 Перша перевірка — нічого не відправляємо.")
                last_alert = is_alert_now
                first_check = False
            elif is_alert_now and not last_alert:
                print("⚠️ Нова тривога! Відправляємо стікер.")
                bot.send_sticker(CHANNEL, ALERT_STICKER)
                last_alert = True
            elif not is_alert_now and last_alert:
                print("✅ Відбій тривоги! Відправляємо стікер.")
                bot.send_sticker(CHANNEL, CLEAR_STICKER)
                last_alert = False

        except Exception as e:
            print(f"❌ Помилка у перевірці: {e}")

        time.sleep(10)

# --- Запуск ---
if __name__ == '__main__':
    print("=== Старт основного процесу ===")
    threading.Thread(target=run_flask).start()
    bot_loop()
