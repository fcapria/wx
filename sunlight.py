#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# LIBRARIES
import logging
import requests, json, gspread
from packaging import version
from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
from google.oauth2.service_account import Credentials
from os import path

# FUNCTIONS

def eastern(dt):
    date_obj = parse(dt)
    return date_obj.astimezone(timezone('America/New_York'))

def ampm(time_string):
    t = datetime.strptime(time_string, "%H:%M:%S")
    return t.strftime("%I:%M:%S %p").lstrip("0")

def daylength(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    durationStr = f"{hours} hours, {minutes} minutes, {seconds} seconds"
    return durationStr

def mmssdelta(secs):
    neg = False
    if secs < 0:
        neg = True
        secs = secs * -1
    mm, ss = divmod(secs, 60)
    if neg:
        mm = mm * -1
    mmssStr = str(mm) + ' minutes, ' + str(ss) + ' seconds'
    return mmssStr

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

# Define log file location (shared across scripts)
log_path = path.join(path.dirname(path.abspath(__file__)), 'wx04849.log')
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,  # Use DEBUG if you want more detail
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# BODY
logging.info("Script:sunlight2.py started.")

# use absolute path to access credentials
filePath = path.abspath(__file__) # full path of this script
dirPath = path.dirname(filePath) # full path of the directory 
jsonFilePath = path.join(dirPath,'wx_secret.json') # absolute json file path

# Use stored credentials for client of the Google Drive API
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(jsonFilePath, scopes=scope)
client = gspread.authorize(creds)

# Sheet shared with weatherman@weather04849.iam.gserviceaccount.com
# Find the workbook by name and open the first sheet
try:
    book = client.open('wx04849')
    sheet = book.worksheet('Sheet1')
except:
    logging.error("Google Sheet did not open.")

# Load config
config_path = path.join(path.dirname(path.abspath(__file__)), 'sunlight2_config.json')
with open(config_path) as f:
    config = json.load(f)
    
LAT = config['latitude']
LON = config['longitude']

# Get the dates
todayDate = datetime.today().strftime('%B %d, %Y')
try:
    try:
        data = solar(LAT,LON,str(todayDate))
    except:
        logging.error("Failed to retrieve solar data.")
        raise

    sunriseIso = data['sunrise']
    sunrise = eastern(sunriseIso)
    sunrise = ampm(sunrise.strftime('%H:%M:%S'))

    sunsetIso = data['sunset']
    sunset = eastern(sunsetIso)
    sunset = ampm(sunset.strftime('%H:%M:%S'))
    dayLength = daylength(data['day_length'])

    todaySec = int(data['day_length'])
    stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    if version.parse(gspread.__version__) >= version.parse("6.0.0"):
        sheet.update([[str(todayDate)]], 'A1')
        sheet.update([[sunrise], [sunset], [dayLength]],'B3:B5')
        sheet.update([[stamp]],'D3')
    else:
        sheet.update('A1', [[str(todayDate)]])
        sheet.update('B3:B5', [[sunrise], [sunset], [dayLength]])
        sheet.update('D3', [[stamp]])


    logging.info("Script:sunlight2.py completed.")

except Exception as e:
    logging.exception("Script:sunlight2.py failed during execution.")