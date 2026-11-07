#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# LIBRARIES
import logging
import sys
import requests, json, gspread
from datetime import datetime
from zoneinfo import ZoneInfo
from google.oauth2.service_account import Credentials
from os import path

# FUNCTIONS

def eastern(isoStr):
    return datetime.fromisoformat(isoStr).astimezone(ZoneInfo('America/New_York'))

def daylength(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    durationStr = f"{hours} hours, {minutes} minutes, {seconds} seconds"
    return durationStr

"""
Example queires to sunrise-sunset.org

https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400
https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400&date=today
https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400&date=2024-01-06
https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400&formatted=0

"""

def solar(lat, lon, dateStr):
    url = 'https://api.sunrise-sunset.org/json'
    params = {
        'lat': lat,
        'lng': lon,
        'date': dateStr,
        'formatted': 0
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data['status'] != 'OK':
            raise ValueError(f"API error: {data['status']}")
        return data['results']
    
    except (requests.RequestException, ValueError, KeyError) as e:
        raise RuntimeError(f"Error retrieving solar data: {e}")


# INITIALIZATIONS

from wx_util import initLogging
initLogging("sunlight.py")

# BODY

# use absolute path to access credentials
filePath = path.abspath(__file__) # full path of this script
dirPath = path.dirname(filePath) # full path of the directory 
jsonFilePath = path.join(dirPath,'wx_secret.json') # absolute json file path

# Use stored credentials for client of the Google Drive API
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(jsonFilePath, scopes=scope)
client = gspread.authorize(creds)

# Sheet shared with weatherman@weather04849.iam.gserviceaccount.com
# Find the workbook by name and open the first sheet
try:
    book = client.open_by_key('17H_sfh2vPotpC_5STXc7eMvWVJd3NaOwI4nJDuhGNtw')
    sheet = book.worksheet('Sheet1')
except Exception:
    logging.exception("Google Sheet did not open.")
    sys.exit(1)

# Load config
config_path = path.join(path.dirname(path.abspath(__file__)), 'sunlight_config.json')
with open(config_path) as f:
    config = json.load(f)
    
LAT = config['latitude']
LON = config['longitude']

# Get the dates
nowEt = datetime.now(ZoneInfo('America/New_York'))
todayDate = nowEt.strftime('%B %d, %Y')
apiDate = nowEt.strftime('%Y-%m-%d')
try:
    data = solar(LAT, LON, apiDate)

    sunrise = eastern(data['sunrise']).strftime('%-I:%M:%S %p')
    sunset = eastern(data['sunset']).strftime('%-I:%M:%S %p')
    dayLength = daylength(data['day_length'])

    stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    sheet.batch_update([
        {'range': 'A1', 'values': [[str(todayDate)]]},
        {'range': 'B3:B5', 'values': [[sunrise], [sunset], [dayLength]]},
        {'range': 'D3', 'values': [[stamp]]},
    ])


    logging.info("===== Finished sunlight.py =====")

except Exception as e:
    logging.exception("sunlight.py failed during execution.")