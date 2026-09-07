from datetime import datetime, timedelta
import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CINEMA_ID = "1072"
PAGE_URL = "https://www.planetcinema.co.il/films/the-odyssey/7460s2r#/buy-tickets-by-film?in-cinema=1072&view-mode=list"

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.planetcinema.co.il/"
    }

    future_date_str = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    api_url = f"https://www.planetcinema.co.il/il/data-api-service/v1/quickbook/10100/dates/in-cinema/{CINEMA_ID}/until/{future_date_str}?attr=&lang=he_IL"

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            return
        
        data = response.json()
        available_dates = data.get("body", {}).get("dates", [])
    except Exception:
        return

    if available_dates:
        dates_list = "\n".join([f"• {d}" for d in available_dates])
        send_telegram_message(
            f"🎬 <b>כל התאריכים שפתוחים כרגע בקולנוע:</b>\n\n"
            f"{dates_list}\n\n"
            f"לינק:\n{PAGE_URL}"
        )

if __name__ == "__main__":
    check_screenings()
