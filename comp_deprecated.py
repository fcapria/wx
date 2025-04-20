#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Frank Capria
April 18, 2020
Based on sunrise.py 
github.com/fcapria/wx
"""

from datetime import datetime
import gspread, logging, json
from google.oauth2.service_account import Credentials
from wx_conversions import getSun
from os import path
from wx_util import initLogging

# body begins
initLogging("comp.py")

filePath = path.abspath(__file__) # full path of this script
dirPath = path.dirname(filePath) # full path of the directory 
jsonFilePath = path.join(dirPath,'wx_secret.json') # absolute json file path


# Load latitude and longitude for ME from sunlight_config.json
sunlightPath = path.join(dirPath, 'sunlight_config.json')
with open(sunlightPath) as f:
    sunlightConfig = json.load(f)
    lat = float(sunlightConfig['latitude'])
    lon = float(sunlightConfig['longitude'])
    mckay = f"lat={lat:.2f}&lng={lon:.2f}"

# Load latitude and longitude for MA from nbro_config.json
nbroPath = path.join(dirPath, 'nbro_config.json')
with open(nbroPath) as f:
    nbroConfig = json.load(f)
    lat = float(nbroConfig['latitude'])
    lon = float(nbroConfig['longitude'])
    overlock = f"lat={lat:.2f}&lng={lon:.2f}"

resultsMe = getSun(mckay)
resultsMa = getSun(overlock)

lengthMe = resultsMe['day_length']
lengthMa = resultsMa['day_length']

meLonger = lengthMe >= lengthMa

dif = abs(lengthMe - lengthMa)

minDif = str((dif) // 60)
secDif = str((dif) % 60)
difString = f"{dif // 60} min {dif % 60} sec"

# use stored credentials for client of the Google Drive API
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(jsonFilePath, scopes=scopes)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.

try:
    sheet = client.open('wx04849').get_worksheet(0)
    # 0 is the index of sheet in workbook
except gspread.exceptions.APIError as ex:
    logging.exception("Google Sheet didn't open for comp.py")

stamp = datetime.now()
sheet.update(
    range_name="A34:E34",
    values=[[
        'Daylight in ME greater by' if meLonger else 'Daylight in MA greater by',
        difString,
        '',
        stamp.strftime("%Y-%m-%d %H:%M:%S"),
        'Called daily by comp.py'
    ]]
)

logging.info(f"Updated daylight comparison {stamp}")
