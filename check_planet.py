from datetime import datetime, timedelta
import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CINEMA_ID = "1072"
FILM_ID = "7460s2r"
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
    dates_api = f"https://www.planetcinema.co.il/il/data-api-service/v1/quickbook/10100/dates/in-cinema/{CINEMA_ID}/until/{future_date_str}?attr=&lang=he_IL"

    try:
        res = requests.get(dates_api, headers=headers)
        if res.status_code != 200:
            return
        dates = res.json().get("body", {}).get("dates", [])
    except Exception:
        return

    imax_screenings = {}

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

                # סינון לפי פורמט IMAX
                attributes = ev.get("attributeIds", [])
                types = ev.get("types", [])
                is_imax = "imax" in [str(a).lower() for a in attributes] or "imax" in [str(t).lower() for t in types]
                
                if not is_imax:
                    continue

                dt_str = ev.get("eventDateTime", "")
                if dt_str:
                    date_part, time_part = dt_str.split("T")
                    hour = time_part[:5]
                    imax_screenings.setdefault(date_part, []).append(hour)
        except Exception:
            continue

    if imax_screenings:
        lines = ["🎬 <b>הקרנות IMAX בלבד עבור האודיסאה:</b>\n"]
        for d in sorted(imax_screenings.keys()):
            hours = ", ".join(sorted(set(imax_screenings[d])))
            lines.append(f"📅 <b>{d}:</b> {hours}")
        lines.append(f"\n{PAGE_URL}")
        send_telegram_message("\n".join(lines))
    else:
        send_telegram_message("לא נמצאו הקרנות IMAX פתוחות כרגע עבור הסרט.")

if __name__ == "__main__":
    check_screenings()
