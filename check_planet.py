from datetime import datetime, timedelta
import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

MOVIE_URL = os.environ.get(
    "MOVIE_URL", 
    "https://www.planetcinema.co.il/films/the-odyssey/7460s2r#/buy-tickets-by-film?in-cinema=1072&view-mode=list"
)

def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(telegram_url, json=payload)

def check_screenings():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(MOVIE_URL, headers=headers)
    if response.status_code != 200:
        return

    content = response.text

    today = datetime.now()
    days_until_thursday = (3 - today.weekday()) % 7
    if days_until_thursday == 0:
        days_until_thursday = 7
    next_thursday = today + timedelta(days=days_until_thursday)

    date_formats = ["07/09", "07/09/2026", "2026-09-07"]

    found = any(fmt in content for fmt in date_formats)

    if found:
        send_telegram_message("✅ בדיקת אימות הצליחה! הסקריפט רואה את התאריכים.")

if __name__ == "__main__":
    check_screenings()
