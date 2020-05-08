#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Dark Sky calls

import requests, json, time, gspread
from tinydb import TinyDB, Query
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from dark_api import APIkey
from wx_conversions import degrees2dir

darkSky = 'https://api.darksky.net/forecast/'

# Define APIkey in dark_api.py and store in same directory as this script

nbroLoc = '/42.3305976,-71.6352203'
lincLoc = '/44.4278389,-69.0088705' 
excludes = '?exclude=flags,minutely,hourly,daily'
darkCall = darkSky + APIkey + lincLoc + excludes
darkCallNbro = darkSky + APIkey + nbroLoc + excludes
suffix = '°F'

try:
    data = requests.get(darkCall)
    dataNbro = requests.get(darkCallNbro)
    dataJSON = data.json()
    dataNbroJSON = dataNbro.json()
    wx = dataJSON['currently']
    wxNbro = dataNbroJSON['currently']
    #summary = wx['summary']
    temp = int(round(wx['temperature'],0))
    tempNbro = int(round(wxNbro['temperature'],0))
    diff = tempNbro - temp
    absDiff = abs(diff)
    absStr = str(absDiff) + suffix
    equalTemp = False
    if diff > 0:
        greaterTemp = 'MA warmer by '
    elif diff < 0:
        greaterTemp = 'ME warmer by '
    else:
        greaterTemp = 'ME and MA are the same temperature.'
        equalTemp = True

except:
    greaterTemp = 'Unable to calculate temperatures'
    
# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('wx_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.   

try:
    sheet = client.open('wx04849').sheet1
    stamp = str(datetime.now())
    sheet.update_cell(35,4,str(stamp))
    sheet.update_cell(35,1,greaterTemp)
    if not equalTemp:
        sheet.update_cell(35,2,absStr)

except:
    print("Sheet didn't open for dark_comp.py")