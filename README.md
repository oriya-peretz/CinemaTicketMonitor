# CinemaTicketMonitor
A lightweight, automated cinema screening monitor built for personal use.

## Overview
This repository contains a personal automated pipeline designed specifically to track screening times for **"The Odyssey"** at **Yes Planet Cinema (Rishon LeZion)** in **IMAX** format.

The project runs via GitHub Actions on an hourly schedule, queries Planet Cinema's API directly, and sends instant Telegram notifications whenever new screening slots or dates open up.

> **Note:** This project is intended strictly for personal tracking purposes and is tailored specifically to monitor IMAX screenings for this specific film.

## How It Works
1. **GitHub Actions Scheduler:** Triggers `check_planet.py` hourly.
2. **API Event Query:** Fetches real-time schedules directly from Planet Cinema's internal endpoints.
3. **Delta Detection:** Compares current IMAX slots against `screenings_state.json` to prevent duplicate alerts.
4. **Telegram Alert:** Sends a formatted notification with direct booking links exclusively when new slots appear.

## Stack
- Python 3.11 (`requests`)
- GitHub Actions (cron + commit persistence)
- Telegram Bot API
