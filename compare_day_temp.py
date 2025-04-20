#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, gspread, json, logging
from datetime import datetime
from google.oauth2.service_account import Credentials
from wx_conversions import getSun
from open_api import openKey
from wx_util import initLogging
from os import path

def gen_state(cur, last):
    d = cur - last
    if -0.1 < d < 0.1:
        return 'Steady'
    elif d > 0:
        return 'Rising'
    else:
        return 'Falling'

# Init logging
initLogging("compare_daylight_temp.py")

# Set up file paths
filePath = path.abspath(__file__)
dirPath = path.dirname(filePath)
jsonFilePath = path.join(dirPath, 'wx_secret.json')

# Load coordinates from config
with open(path.join(dirPath, 'sunlight_config.json')) as f:
    meConfig = json.load(f)
    meLoc = f"lat={float(meConfig['latitude']):.2f}&lng={float(meConfig['longitude']):.2f}"

with open(path.join(dirPath, 'nbro_config.json')) as f:
    maConfig = json.load(f)
    maLoc = f"lat={float(maConfig['latitude']):.2f}&lng={float(maConfig['longitude']):.2f}"

# Call sunrise-sunset API
resultsMe = getSun(meLoc)
resultsMa = getSun(maLoc)
lengthMe = resultsMe['day_length']
lengthMa = resultsMa['day_length']
meLonger = lengthMe >= lengthMa
dif = abs(lengthMe - lengthMa)
difString = f"{dif // 60} min {dif % 60} sec"

# Call OpenWeather API
openwx = "https://api.openweathermap.org/data/3.0/onecall?lat="
units = "&units=imperial"
excludes = "&exclude=minutely,hourly,daily,alerts"
key = f"&appid={openKey}"

lCall = f"{openwx}{meConfig['latitude']}&lon={meConfig['longitude']}{units}{excludes}{key}"
nCall = f"{openwx}{maConfig['latitude']}&lon={maConfig['longitude']}{units}{excludes}{key}"

equalTemp = False
try:
    lResp = requests.get(lCall)
    nResp = requests.get(nCall)
    lData = lResp.json()["current"]
    nData = nResp.json()["current"]

    lTemp = round(lData["temp"])
    nTemp = round(nData["temp"])
    diff = nTemp - lTemp

    if diff > 0:
        tempMsg = "MA warmer by "
    elif diff < 0:
        tempMsg = "ME warmer by "
    else:
        tempMsg = "ME and MA temperatures are equal."
        equalTemp = True

    diffStr = f"{abs(diff)}°F" if not equalTemp else "-"
except Exception as ex:
    tempMsg = "Unable to calculate temperature"
    diffStr = "-"
    logging.error(f"OpenWeather API request failed: {ex}", exc_info=True)

# Open Google Sheet
try:
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(jsonFilePath, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open('wx04849').sheet1
except Exception as ex:
    logging.exception("Google Sheet failed to open.")
    sys.exit(1)

# Write daylight comparison (Row 34)
stamp = datetime.now()
sheet.update(
    range_name="A34:E35",
    values=[
        [
            "Daylight in ME greater by" if meLonger else "Daylight in MA greater by",
            difString,
            "",
            stamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Called by compare_day_temp.py"
        ],
        [
            tempMsg,
            diffStr,
            "",
            "",
            "Using: Sunrise-Sunset.org, OpenWeather"
        ]
    ]
)
