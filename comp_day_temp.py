#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Frank Capria
April 2025
Combined daylight and temperature comparison
github.com/fcapria/wx
"""

from datetime import datetime
import gspread, logging, json, requests
from os import path
from wx_conversions import getSun
from wx_util import initLogging
from google.oauth2.service_account import Credentials
from open_api import openKey

# Initialize logging
initLogging("compare_daylight_temp.py")

# === Setup paths ===
filePath = path.abspath(__file__)
dirPath = path.dirname(filePath)
jsonPath = path.join(dirPath, 'wx_secret.json')
sunlightConfigPath = path.join(dirPath, 'sunlight_config.json')
nbroConfigPath = path.join(dirPath, 'nbro_config.json')

# === Load lat/lon for ME and MA ===
with open(sunlightConfigPath) as f:
    sunlightConfig = json.load(f)
    meLat = float(sunlightConfig['latitude'])
    meLon = float(sunlightConfig['longitude'])

with open(nbroConfigPath) as f:
    nbroConfig = json.load(f)
    maLat = float(nbroConfig['latitude'])
    maLon = float(nbroConfig['longitude'])

meCoordStr = f"lat={meLat:.2f}&lng={meLon:.2f}"
maCoordStr = f"lat={maLat:.2f}&lng={maLon:.2f}"

# === Get daylight info ===
resultsMe = getSun(meCoordStr)
resultsMa = getSun(maCoordStr)

lengthMe = resultsMe['day_length']
lengthMa = resultsMa['day_length']
meLonger = lengthMe >= lengthMa
dif = abs(lengthMe - lengthMa)
difString = f"{dif // 60} min {dif % 60} sec"

# === Get temperature info from OpenWeather ===
openwx = 'https://api.openweathermap.org/data/3.0/onecall?lat='
units = '&units=imperial'
excludes = '&exclude=minutely,hourly,daily,alerts'
key = '&appid=' + openKey

suffix = '°F'
equalTemp = False

try:
    meCall = openwx + str(meLat) + '&lon=' + str(meLon) + units + excludes + key
    maCall = openwx + str(maLat) + '&lon=' + str(maLon) + units + excludes + key

    meJSON = requests.get(meCall).json()
    maJSON = requests.get(maCall).json()

    meTemp = int(round(meJSON['current']['temp'], 0))
    maTemp = int(round(maJSON['current']['temp'], 0))

    diff = maTemp - meTemp
    if diff > 0:
        tempSummary = 'MA warmer by '
    elif diff < 0:
        tempSummary = 'ME warmer by '
    else:
        tempSummary = 'ME and MA temperatures are equal.'
        equalTemp = True

    tempDiffStr = '-' if equalTemp else str(abs(diff)) + suffix

except requests.exceptions.RequestException as e:
    logging.exception("Error retrieving temperature data.")
    tempSummary = 'Unable to calculate temperature'
    tempDiffStr = '-'

# === Connect to Google Sheets ===
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(jsonPath, scopes=scopes)
client = gspread.authorize(creds)

try:
    sheet = client.open('wx04849').sheet1
    now = datetime.now()

    # Update daylight comparison (Row 34)
    sheet.update(
        range_name="A34:E34",
        values=[[
            'Daylight in ME greater by' if meLonger else 'Daylight in MA greater by',
            difString,
            '',
            now.strftime("%Y-%m-%d %H:%M:%S"),
            'Uses OpenWeather and Sunrise-Sunset.org'
        ]]
    )

    # Update temperature comparison (Row 35)
    sheet.update(
        range_name="A35:E35",
        values=[[
            tempSummary,
            tempDiffStr,
            '',
            '',
            'Called by: comp_day_temp.py'
        ]]
    )
    logging.info("Updated temperature comparison")

except gspread.exceptions.APIError as e:
    logging.exception("Error writing to Google Sheet.")
