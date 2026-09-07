from datetime import datetime, timedelta
import json
import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CINEMA_ID = "1072"
FILM_ID = "7460s2r"
PAGE_URL = "https://www.planetcinema.co.il/films/the-odyssey/7460s2r#/buy-tickets-by-film?in-cinema=1072&view-mode=list"
STATE_FILE = "screenings_state.json"

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
    dates_api = f"https://www.planetcinema.co.il/il/data-api-service/v1/quickbook/10100/dates/in-cinema/{CINEMA_ID}/until/{future_date_str}?attr=&lang=he_IL"

    try:
        res = requests.get(dates_api, headers=headers)
        if res.status_code != 200:
            return
        dates = res.json().get("body", {}).get("dates", [])
    except Exception:
        return

    current_imax = {}

    for d in dates:
        film_events_api = f"https://www.planetcinema.co.il/il/data-api-service/v1/quickbook/10100/film-events/in-cinema/{CINEMA_ID}/at-date/{d}?filmId={FILM_ID}&lang=he_IL"
        try:
            r = requests.get(film_events_api, headers=headers)
            if r.status_code != 200:
                continue
            events = r.json().get("body", {}).get("events", [])
            for ev in events:
                ev_film_id = ev.get("filmId") or ev.get("compositeFilmId")
                if ev_film_id != FILM_ID:
                    continue

                attributes = ev.get("attributeIds", [])
                types = ev.get("types", [])
                is_imax = "imax" in [str(a).lower() for a in attributes] or "imax" in [str(t).lower() for t in types]

                if not is_imax:
                    continue

                dt_str = ev.get("eventDateTime", "")
                if dt_str:
                    date_part, time_part = dt_str.split("T")
                    hour = time_part[:5]
                    current_imax.setdefault(date_part, []).append(hour)
        except Exception:
            continue

    known_imax = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                known_imax = json.load(f)
        except Exception:
            known_imax = {}

    new_screenings = {}
    for d, times in current_imax.items():
        known_times = set(known_imax.get(d, []))
        diff = set(times) - known_times
        if diff:
            new_screenings[d] = sorted(list(diff))

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(current_imax, f, ensure_ascii=False, indent=2)

    if new_screenings:
        lines = ["🚨 <b>נפתחו הקרנות IMAX חדשות להאודיסאה!</b>\n"]
        for d in sorted(new_screenings.keys()):
            hours = ", ".join(new_screenings[d])
            lines.append(f"📅 <b>{d}:</b> {hours}")
        lines.append(f"\nלינק להזמנה:\n{PAGE_URL}")
        send_telegram_message("\n".join(lines))

if __name__ == "__main__":
    check_screenings()
