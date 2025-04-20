#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, json, time, gspread, logging
from datetime import datetime
from google.oauth2.service_account import Credentials
from open_api import openKey
from wx_util import initLogging

def gen_state(cur,last):
    d = cur - last
    if d > -0.1 and d < 0.1:
        msg = 'Steady'
    elif d > 0:
        msg = 'Rising'
    else:
        msg = 'Falling'
    return msg

initLogging("compare.py")

openwx = 'https://api.openweathermap.org/data/3.0/onecall?lat='
lLat = '44.4278389'
lLon = '&lon=-69.0088705'
nLat = '42.3305976'
nLon = '&lon=-71.6352203'
units = '&units=imperial'
excludes = '&exclude=minutely,hourly,daily,alerts'
key = '&appid='+ openKey

equalTemp = False

lOpenCall = openwx + lLat + lLon + units + excludes + key
nOpenCall = openwx + nLat + nLon + units + excludes + key

suffix = '°F'

try:
    lData = requests.get(lOpenCall)
    nData = requests.get(nOpenCall)
    lJSON = lData.json()
    nJSON = nData.json()
    
    lData = lJSON['current']
    nData = nJSON['current']
    
    lTemp = int(round(lData['temp'],0))
    lString = str(lTemp) + suffix
    nTemp = int(round(nData['temp'],0))
    nString = str(nTemp) + suffix
    
    diff = nTemp - lTemp
    if diff > 0:
        greaterTemp = 'MA warmer by '
    elif diff < 0:
        greaterTemp = 'ME warmer by '
    else:
        greaterTemp = 'ME and MA temperatures are equal.'
        equalTemp = True
        
except requests.exceptions as ex:
    greaterTemp = 'Unable to calculate temperature'
    logging.error(f"OpenWeather API request failed: {ex}", exc_info=True)
    
# use creds to create a client to interact with the Google Drive API
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('wx_secret.json', scopes=scopes)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here. 

try:
    sheet = client.open('wx04849').sheet1
    stamp = str(datetime.now())
    sheet.update_cell(35,4,str(stamp))
    sheet.update_cell(35,5,'Called by compare.py')
    sheet.update_cell(35,1,greaterTemp)
    if diff < 0:
        diff = diff *-1
    
    diffStr = str(diff) + suffix
    if not equalTemp:
        sheet.update_cell(35,2,diffStr)
    else:
        sheet.update_cell(35,2,'-')
    #cell = sheet.find('Current temperature')
    #sheet.update_cell(cell.row,cell.col+3,tempStatus)
    #sheet.update_cell(cell.row+5,cell.col+3,windStatus)
    logging.info("Google Sheet updated with:")
    logging.info(f"  Temp Diff: {diffStr if not equalTemp else '-'}")
    logging.info(f"  Stamp: {stamp}")

    logging.info(f"compare.py complete: {stamp}")
except gspread.exceptions.APIError as ex:
    logging.exception("Google Sheet didn't open for compare.py")
    
