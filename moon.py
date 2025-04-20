#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, json, logging, pytz, gspread, ephem, sys, time
from google.oauth2.service_account import Credentials
from wx_conversions import am_pm
from moon_api import apiKey
from os import path
from datetime import datetime

def get_phase(year, month, day):
    date = ephem.Date(datetime.date(year, month, day))
    nnm = ephem.next_new_moon(date)
    pnm = ephem.previous_new_moon(date)
    lunation = (date - pnm) / (nnm - pnm)
    return lunation

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
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(jsonFilePath, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open('wx04849').sheet1
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
    col = 2
    stamp = today.strftime("%Y-%m-%d %H:%M:%S")
    try:
        logging.info("attempting to stamp")
        sheet.update(values=[[stamp]], range_name=f"D{row}")
        logging.info("updated stamp")
        sheet.update(values=[["Source: ipgeolocation.io"], ["Called by moon.py"]], range_name=f"E{row}:E{row + 1}")
        sheet.update(
            values=[[am_pm(moonrise)], [am_pm(moonset)], [f"{phasePct}%"], [phaseName]],
            range_name=f"B{row}:B{row + 3}"
        )
        sheet.update(values=[["Moon.py was here"]], range_name="Y1")  # Switched from invalid Z1
    except Exception as e:
        logging.exception("Failed to update Google Sheet")
        sys.exit(1)

    logging.info("===== Finished moon.py successfully =====")

if __name__ == "__main__":
    main()
