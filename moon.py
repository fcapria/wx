#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, json, logging, gspread, ephem, sys, time
from google.oauth2.service_account import Credentials
from wx_conversions import am_pm
from moon_api import apiKey
from os import path
from datetime import datetime


def definePhase(date):
    ephDate = ephem.Date(date)
    moonToday = ephem.Moon(ephDate)
    illumToday = moonToday.phase
    moonYesterday = ephem.Moon(ephDate - 1)
    illumYesterday = moonYesterday.phase
    waxing = illumToday > illumYesterday

    if illumToday < 1.0:
        return "New Moon"
    elif illumToday < 49.0:
        return "Waxing Crescent" if waxing else "Waning Crescent"
    elif 49.0 <= illumToday <= 51.0:
        return "First Quarter" if waxing else "Last Quarter"
    elif illumToday < 98.0:
        return "Waxing Gibbous" if waxing else "Waning Gibbous"
    else:
        return "Full Moon"

def main():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logPath = path.join(path.dirname(path.abspath(__file__)), 'wx04849.log')

    logging.basicConfig(
        filename=logPath,
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    logging.info("===== Starting moon.py =====")

    attempts = 0
    maxAttempts = 4
    response = None

    today = datetime.now()
    fullDt = today.strftime('%Y-%m-%d')

    base = 'https://api.ipgeolocation.io/astronomy?apiKey='
    latLong = '&lat=44.308&long=-69.051'
    date = '&date=' + fullDt
    call = base + apiKey + latLong + date

    while attempts < maxAttempts:
        try:
            response = requests.get(call, timeout=10)
            response.raise_for_status()
            logging.info(f"Successfully connected to ipgeolocation.com on attempt {attempts + 1}")
            break
        except requests.exceptions.RequestException as ex:
            attempts += 1
            logging.warning(f"Attempt {attempts} failed to reach ipgeolocation.com")
            logging.exception(ex)
            time.sleep(2 * attempts)
    else:
        logging.error("All retry attempts to ipgeolocation failed")
        sys.exit(1)

    filePath = path.abspath(__file__)
    dirPath = path.dirname(filePath)
    jsonFilePath = path.join(dirPath, 'wx_secret.json')

    try:
        data = json.loads(response.text)
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(jsonFilePath, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key('17H_sfh2vPotpC_5STXc7eMvWVJd3NaOwI4nJDuhGNtw').sheet1
    except (json.JSONDecodeError, gspread.exceptions.APIError, Exception) as ex:
        logging.exception("Failed to initialize Google Sheet or parse API data")
        sys.exit(1)

    moonrise = data.get("moonrise", "Missing")
    moonset = data.get("moonset", "Missing")

    ephToday = ephem.Date(today)
    moonToday = ephem.Moon()
    moonToday.compute(ephToday)

    phasePct = round(moonToday.phase, 1)
    phaseName = definePhase(today)

    row = 6
    stamp = today.strftime("%Y-%m-%d %H:%M:%S")
    try:
        logging.info("attempting to stamp")
        sheet.batch_update([
            {'range': f"D{row}", 'values': [[stamp]]},
            {'range': f"E{row}:E{row + 1}", 'values': [["Source: ipgeolocation.io"], ["Called by moon.py"]]},
            {'range': f"B{row}:B{row + 2}", 'values': [[am_pm(moonrise)], [am_pm(moonset)], [phaseName]]},
            {'range': "Y1", 'values': [["Moon.py was here"]]},  # Switched from invalid Z1
        ])
        logging.info("updated stamp")
    except Exception as e:
        logging.exception("Failed to update Google Sheet")
        sys.exit(1)

    logging.info("===== Finished moon.py successfully =====")

if __name__ == "__main__":
    main()
