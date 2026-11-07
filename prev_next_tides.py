#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prev_next_tides.py

Fetches the most recent past tide event and the next upcoming tide event
for Rockland, ME (station 8415490) and writes them to the 'tides' tab
of the wx04849 Google Sheet.

Layout:
    B2: prev type (High / Low)
    C2: prev height (e.g. "5 ft 4 in")
    D2: prev timestamp (e.g. "6:42 AM")
    B3: next type
    C3: next height
    D3: next timestamp

Frank Capria
"""

import logging, math, requests, gspread, warnings
warnings.filterwarnings("ignore", category=UserWarning, module="gspread")
from datetime import datetime
from google.oauth2.service_account import Credentials
from os import path
from wx_conversions import am_pm, yesterday_int


def get_sheet() -> gspread.Worksheet:
    scriptDir = path.dirname(path.abspath(__file__))
    jsonPath = path.join(scriptDir, "wx_secret.json")
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(jsonPath, scopes=scope)
    client = gspread.authorize(creds)
    try:
        return client.open_by_key('17H_sfh2vPotpC_5STXc7eMvWVJd3NaOwI4nJDuhGNtw').worksheet('tides')
    except Exception as e:
        raise RuntimeError(f"Failed to open 'tides' sheet: {e}")


def ft_to_ft_in(ft_str: str) -> str:
    total_in = round(float(ft_str) * 12)
    sign = '-' if total_in < 0 else ''
    feet, inches = divmod(abs(total_in), 12)
    return f"{sign}{inches} in" if sign and feet == 0 else f"{sign}{feet} ft {inches} in"


def tide_type(code: str) -> str:
    return "High" if code == "H" else "Low"


def fmt_time(t_str: str) -> str:
    # t_str is "YYYY-MM-DD HH:MM"
    time_part = t_str.split(' ')[1]
    return am_pm(time_part)


def fetch_tides() -> list:
    station = '8415490'
    name = 'Frank.Capria'
    begin_date = str(yesterday_int())
    base_url = 'https://tidesandcurrents.noaa.gov/api/'
    url = (
        f"{base_url}datagetter?product=predictions"
        f"&application={name}&begin_date={begin_date}&range=72"
        f"&datum=MLLW&station={station}"
        f"&time_zone=lst_ldt&units=english&interval=hilo&format=JSON"
    )
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json().get('predictions', [])


def estimate_current_height(prev_event, next_event) -> str:
    now = datetime.now()
    t_prev = datetime.strptime(prev_event['t'], "%Y-%m-%d %H:%M")
    t_next = datetime.strptime(next_event['t'], "%Y-%m-%d %H:%M")
    h_prev = float(prev_event['v'])
    h_next = float(next_event['v'])
    fraction = (now - t_prev).total_seconds() / (t_next - t_prev).total_seconds()
    height = h_prev + (h_next - h_prev) * (1 - math.cos(math.pi * fraction)) / 2
    return ft_to_ft_in(str(height))


def find_prev_next(tides: list):
    now = datetime.now()
    prev_event = None
    next_event = None

    for tide in tides:
        tide_dt = datetime.strptime(tide['t'], "%Y-%m-%d %H:%M")
        if tide_dt <= now:
            prev_event = tide
        elif next_event is None:
            next_event = tide
            break

    return prev_event, next_event


def main():
    logging.basicConfig(
        filename='wx04849.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )
    logging.info("===== Starting prev_next_tides.py =====")

    try:
        tides = fetch_tides()
        logging.info(f"Fetched {len(tides)} tide events from NOAA API.")
    except Exception as e:
        logging.error(f"Failed to fetch tide data: {e}")
        return

    prev_event, next_event = find_prev_next(tides)

    if not prev_event or not next_event:
        logging.warning("Could not determine both prev and next tide events. Exiting.")
        return

    try:
        sheet = get_sheet()
    except RuntimeError as e:
        logging.error(e)
        return

    rows = [
        [tide_type(prev_event['type']), ft_to_ft_in(prev_event['v']), fmt_time(prev_event['t'])],
        [tide_type(next_event['type']), ft_to_ft_in(next_event['v']), fmt_time(next_event['t'])],
    ]

    current_height = estimate_current_height(prev_event, next_event)

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.batch_update([
        {'range': 'B2:D3', 'values': rows},
        {'range': 'B4', 'values': [[current_height]]},
        {'range': 'B5', 'values': [[stamp]]},
    ])
    logging.info(f"Updated tides sheet: prev={rows[0]}, next={rows[1]}")
    logging.info("===== prev_next_tides.py complete =====")


if __name__ == "__main__":
    main()
