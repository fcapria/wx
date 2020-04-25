#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Frank Capria
April 18, 2020
Based on sunrise.py 
github.com/fcapria/wx
"""

import requests, json, calendar, gspread
from datetime import datetime
from pytz import timezone
import iso8601 as iso 
from dateutil import parser
from oauth2client.service_account import ServiceAccountCredentials
from tinydb import TinyDB, Query
from wx_conversions import getSun

# Now that these functions are in two scripts, they need to be
# placed in wx_conversions

def time_string_to_minutes(t):
    #print(t)
    tString = t.split(':')
    hrs = int(tString[0])
    mns = int(tString[1])
    daylightMins = (hrs*60) + mns
    return daylightMins

def mins_to_hours_and_mins(i):
    hrs = i / 60
    mins = i % 60
    string = str(hrs) + ' hours' + str(mins) + ' minutes'
    return string

def datestr(dt):
   yr = dt[:4]
   mo = calendar.month_name[int(dt[5:7])]
   date = dt[8:10]
   dtStr = mo + ' ' + date + ', ' + yr
   return(dtStr)

def eastern(dt):
    dateObj = iso.parse_date(dt)
    dateEastern = dateObj.astimezone(timezone('US/Eastern'))
    return(dateEastern)

def length(seconds):
    seconds = int(seconds)
    hours = (seconds // 3600)
    minutes = ((seconds / 3600) - hours) * 60
    minutes = int(minutes // 1)
    hrString = str(hours) + ' hours '
    mnString = str(minutes) + ' minutes'
    daylight = hrString + mnString
    return daylight
  
# body begins

mckay = "lat=44.31&lng=-69.05"
resultsMe = getSun(mckay)
overlock = "lat=42.33&lng=-71.64"
resultsMa = getSun(overlock)

lengthMe = resultsMe['day_length']
lengthMa = resultsMa['day_length']

if lengthMe >= lengthMa:
    meLonger = True
else:
    meLonger = False

dif = lengthMe - lengthMa
if dif < 0:
    dif = dif * -1

minDif = str((lengthMe - lengthMa) // 60)
secMod = str((lengthMe - lengthMa) % 60)
difString = str(minDif + ' min ' + secMod + ' sec')

# use stored credentials for client of the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('wx_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.

try:
    sheet = client.open('wx04849').get_worksheet(0)
    # 0 is the index of sheert in workbook
except:
    print ('Google Sheet did not open.')

if meLonger:
    sheet.update_cell(34,1,'Daylight in ME greater by')
else:
    sheet.update_cell(34,1,'Daylight in MA greater by')

sheet.update_cell(34,2,difString)

stamp = datetime.now()
sheet.update_cell(34,4,str(stamp))
sheet.update_cell(34,5,'Source: sunrise-sunset.org')
sheet.update_cell(35,5,'Called by: comp.py')

print('Updated daylight comparison ',str(stamp))