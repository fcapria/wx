#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime, requests, json, time, pytz, gspread, ephem, logging
from oauth2client.service_account import ServiceAccountCredentials
from wx_conversions import am_pm
from moon_api import apiKey
from os import path

def setup_logging(logFilePath):
    logging.basicConfig(
        filename=logFilePath,
        filemode='a',
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.INFO
    )
    return logging.getLogger('moon_logger')

def get_phase(year, month, day):
    date = ephem.Date(datetime.date(year, month, day))
    nnm = ephem.next_new_moon(date)
    pnm = ephem.previous_new_moon(date)
    return (date - pnm) / (nnm - pnm)

def define_phase(lunation):
    if lunation < 0.03 or lunation > 0.97:
        return 'New'
    elif lunation < 0.22:
        return 'Waxing Cresent'
    elif lunation < 0.28:
        return 'First Quarter'
    elif lunation < 0.47:
        return 'Waxing Gibbous'
    elif lunation < 0.53:
        return 'Full'
    elif lunation < 0.72:
        return 'Waning Gibbous'
    elif lunation < 0.78:
        return 'Last Quarter'
    else:
        return 'Waning Cresent'

def parse_moon_times(moonriseStr, moonsetStr, dateStr, tzName='America/New_York'):
    tz = pytz.timezone(tzName)
    baseDate = datetime.datetime.strptime(dateStr, '%Y-%m-%d')

    riseHour, riseMin = map(int, moonriseStr.split(':'))
    moonrise = tz.localize(baseDate.replace(hour=riseHour, minute=riseMin))

    setHour, setMin = map(int, moonsetStr.split(':'))
    moonset = tz.localize(baseDate.replace(hour=setHour, minute=setMin))

    if moonset < moonrise:
        moonset += datetime.timedelta(days=1)

    return moonrise, moonset

# Setup path and logging
filePath = path.abspath(__file__)
dirPath = path.dirname(filePath)
logFilePath = path.join(dirPath, 'wx04849.log')
jsonFilePath = path.join(dirPath, 'wx_secret.json')
logger = setup_logging(logFilePath)

# Prepare date and API call
today = datetime.datetime.now()
yr = today.strftime('%Y')
mo = today.strftime('%-m')
dt = today.strftime('%-d')
fullDt = f"{yr}-{mo}-{dt}"

base = 'https://api.ipgeolocation.io/astronomy?apiKey='
latLong = '&lat=44.308&long=-69.051'
call = base + apiKey + latLong

# API request
attempts = 0
error = False
while attempts < 4 and not error:
    attempts += 1
    try:
        response = requests.get(call)
        response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        logger.error('Failed to connect to api.ipgeolocation.com on attempt %d: %s', attempts, ex)
        error = True

if not error:
    data = json.loads(response.text)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(jsonFilePath, scope)
    try:
        client = gspread.authorize(creds)
        sheet = client.open('wx04849').sheet1
    except gspread.exceptions.APIError as ex:
        logger.error("Google Sheet access error: %s", ex)
        error = True

if not error:
    moonriseStr = data['moonrise']
    moonsetStr = data['moonset']
    moonrise, moonset = parse_moon_times(moonriseStr, moonsetStr, fullDt)

    row = 6
    sheet.update_cell(row, 1, 'Moonrise')
    sheet.update_cell(row, 2, am_pm(moonriseStr))
    sheet.update_cell(row, 3, 'tomorrow' if moonrise.date() > today.date() else ' ')
    sheet.update_cell(row, 4, str(datetime.datetime.now()))
    sheet.update_cell(row, 5, 'Source:ipgeolocation.com')

    row += 1
    sheet.update_cell(row, 1, 'Moonset')
    sheet.update_cell(row, 2, am_pm(moonsetStr))
    sheet.update_cell(row, 3, 'tomorrow' if moonset.date() > today.date() else ' ')
    sheet.update_cell(row, 5, 'Called by: moon.py')

    row += 1
    sheet.update_cell(row, 1, 'Phase')
    lunation = get_phase(int(yr), int(mo), int(dt))
    sheet.update_cell(row, 2, define_phase(lunation))

    logger.info('moon.py completed successfully')
else:
    logger.error('moon.py completed with error(s)')
ew