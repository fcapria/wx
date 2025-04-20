#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# OpenWeather OneCall API Script for Current Conditions
# Updated to use modern gspread authentication

import requests, gspread, json, logging, sys
from datetime import datetime
from wx_conversions import degrees2dir, meters2miles
from os import path
from open_api import openKey
from wx_util import initLogging

def safe_get(data, key, formatter=str, suffix=''):
    try:
        return f"{formatter(data[key])}{suffix}"
    except Exception:
        return MISS

def safe_wind_dir(data):
    try:
        return degrees2dir(data['wind_deg'])
    except Exception:
        return MISS

# Load latitude and longitude from config
configPath = path.join(path.dirname(path.abspath(__file__)), 'sunlight_config.json')
with open(configPath, 'r') as f:
    config = json.load(f)
    LAT = config['latitude']
    LON = config['longitude']

MISS = 'Missing'

openCall = (
    f"https://api.openweathermap.org/data/3.0/onecall?"
    f"lat={LAT}&lon={LON}&units=imperial"
    f"&exclude=minutely,hourly,daily,alerts"
    f"&appid={openKey}"
)

def main():
    initLogging("open2.py")

    filePath = path.abspath(__file__)
    dirPath = path.dirname(filePath)
    jsonFilePath = path.join(dirPath, 'wx_secret.json')

    try:
        openData = requests.get(openCall)
        openData.raise_for_status()
        openJSON = openData.json()
        data = openJSON['current']
        logging.info("Successfully fetched OpenWeather data.")
    except Exception:
        logging.exception("Failed to fetch or parse 'current' field from OpenWeather API response JSON.")
        sys.exit(1)

    try:
        client = gspread.service_account(filename=jsonFilePath)
        sheet = client.open('wx04849').sheet1
    except Exception:
        logging.exception("Google Sheet didn't open when called by open2.py")
        sys.exit(1)

    # Extract and safely format weather fields
    currentCond = data.get('weather', [{}])[0].get('description', MISS)
    temp = safe_get(data, 'temp', lambda x: round(x, 1), "°F")
    dew = safe_get(data, 'dew_point', lambda x: round(x, 1), "°F")
    humid = safe_get(data, 'humidity', str, "%")
    feels = safe_get(data, 'feels_like', lambda x: round(x, 1), "°F")
    windDir = safe_wind_dir(data)
    windSpeed = safe_get(data, 'wind_speed', lambda x: round(x, 1), " MPH")
    windGust = safe_get(data, 'wind_gust', lambda x: round(x, 1), " MPH")
    vis = safe_get(data, 'visibility', meters2miles)

    weatherValues = [
        currentCond,
        temp,
        dew,
        humid,
        feels,
        windDir,
        windSpeed,
        windGust,
        vis
    ]

    row = 9
    col = 2
    stamp = str(datetime.now())
    sheet.update_cell(row, 4, stamp)
    sheet.update_cell(row, 5, 'Source: Open Weather')
    sheet.update_cell(row + 1, 5, 'Called by open2.py')

    for value in weatherValues:
        sheet.update_cell(row, col, value)
        row += 1

    logging.info("===== open2.py completed successfully. =====")

if __name__ == "__main__":
    main()
