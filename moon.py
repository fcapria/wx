#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime, requests, json, logging, pytz, gspread, ephem
from oauth2client.service_account import ServiceAccountCredentials
from wx_conversions import am_pm
from moon_api import apiKey
from os import path

def get_phase(year,month,day):

    """Returns a floating-point number from 0-1. where 0=new, 0.5=full, 1=new"""
    
    # Ephem stores its date numbers as floating points, which the following uses
    # to conveniently extract the percent time between one new moon and the next
    # This corresponds (somewhat roughly) to the phase of the moon.
    # Lifted from a tutorial. I would like to credit the author, but lost the link

    # Use Year, Month, Day as arguments
   
    date = ephem.Date(datetime.date(year,month,day))

    nnm = ephem.next_new_moon(date)
    pnm = ephem.previous_new_moon(date)

    lunation=(date-pnm)/(nnm-pnm)

    # There is a ephem.Moon().phase() command, but it can't differentiate 
    # between waxing and waning.

    return lunation

def define_phase(lunation):
    if lunation < 0.03 or lunation > 0.97:
        phase = 'New'
    elif lunation < 0.22:
        phase = 'Waxing Cresent'
    elif lunation < 0.28:
        phase = 'First Quarter'
    elif lunation < 0.47:
        phase = 'Waxing Gibbous'
    elif lunation < 0.53:
        phase = 'Full'
    elif lunation < 0.72:
        phase = 'Waning Gibbous'
    elif lunation < 0.78:
        phase = 'Last Quarter'
    else:
        phase = 'Waning Cresent'
    return phase

# BODY

# Set log file location
logPath = path.join(path.dirname(path.abspath(__file__)), 'wx04849.log')

logging.basicConfig(
    filename=logPath,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

logging.info("===== Starting moon.py =====")

today = datetime.datetime.now()
yr = today.strftime('%Y')
mo = today.strftime('%-m')
dt = today.strftime('%-d')
fullDt = yr + '-' + mo + '-' + dt

base = 'https://api.ipgeolocation.io/astronomy?apiKey=' 
# Define apiKey in moon_api.py and store in same directory as this script
latLong = '&lat=44.308&long=-69.051'
date = '&date=' + fullDt
call = base + apiKey + latLong

attempts = 0
error = False
while attempts < 4 and not error: 
    attempts += 1
    try:
        response = requests.get(call)
    except requests.exceptions.RequestException as ex:  
        error = True
        logging.error("Failed to connect to ipgeolocation.com")
        logging.exception(ex)

#Set absolute path
filePath = path.abspath(__file__) # full path of this script
dirPath = path.dirname(filePath) # full path of the directory 
jsonFilePath = path.join(dirPath,'wx_secret.json') # absolute json file path    

if not error:
    data = json.loads(response.text)
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(jsonFilePath, scope)
    client = gspread.authorize(creds)
    try:
        client = gspread.authorize(creds)
        sheet = client.open('wx04849').sheet1
    except gspread.exceptions.APIError as ex:
        print(ex)
        logging.error("Google Sheet did not open in moon.py")
        error = True
if not error:      
    row = 6
    sheet.update_cell(row,1,'Moonrise')
    time12 = am_pm(data['moonrise'])
    sheet.update_cell(row,2,time12)
    sheet.update_cell(row,4,str(datetime.datetime.now()))
    sheet.update_cell(row,5,'Source:ipgeolocation.com')
    row += 1
    sheet.update_cell(row,1,'Moonset')
    time12 = am_pm(data['moonset'])
    sheet.update_cell(row,2,time12)
    sheet.update_cell(row,5,'Called by: moon.py')
    row += 1
    sheet.update_cell(row,1,'Phase')
    # Moon phase
    yr = int(yr)
    mo = int(mo)
    dt = int(dt)
    lunation = get_phase(yr,mo,dt)
    phase = define_phase(lunation)
    sheet.update_cell(row,2,phase)

    logging.info("===== Finished moon.py successfully =====")

else:
    logging.warning("===== moon.py completed with errors =====")



