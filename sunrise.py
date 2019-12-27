#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Frank Capria
November 8, 2019
v 1.0  - Sunrise and sunset information pulled from sunrise-sunset.org
         Writes date, surise, sunset, and day length to Google sheet
November 27, 2019
v 1.01 - Moved timestamp and added source information to sheet



Hard coded for Lincolnville, ME
"""
import requests, json, calendar, gspread
from datetime import datetime
from pytz import timezone
import iso8601 as iso 
from dateutil import parser
from oauth2client.service_account import ServiceAccountCredentials
from wx_conversions import am_pm

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

def getSun(loc):  #need try/excepts for errors

    base = 'https://api.sunrise-sunset.org/json?'
    time = '&formatted=0'
    url = base + loc + time
    
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as ex:
        print(ex)
    
    allData = json.loads(response.text)
    results = allData['results']   
    return(results)
  
# body begins

mckay = "lat=44.31&lng=-69.05"
results = getSun(mckay)

sunriseIso = results['sunrise']
sunrise = eastern(sunriseIso)
sunrise = (sunrise.strftime('%H:%M:%S'))
sunrise = am_pm(sunrise)

sunriseIso = results['sunset']
sunset = eastern(sunriseIso)
sunset = (sunset.strftime('%H:%M:%S'))
sunset = am_pm(sunset)

dayLength = results['day_length']
daylight = length(dayLength)

currentDt = datestr(sunriseIso)

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('wx_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.


try:
    sheet = client.open('wx04849').sheet1
except:
    print ('Google Sheet did not open.')
sheet.update_cell(1,1,currentDt)
row = 3
col = 2
sheet.update_cell(row,1,'Sunrise')
sheet.update_cell(row,2,' ')
sheet.update_cell(row,2,sunrise)
print(sunrise)
row += 1

sheet.update_cell(row,1,'Sunset')
sheet.update_cell(row,2,' ')
sheet.update_cell(row,2,sunset)
print(sunset)
row +=1

sheet.update_cell(row,1,'Daylight')
sheet.update_cell(row,2,' ')
sheet.update_cell(row,2,daylight)

stamp = datetime.now()
sheet.update_cell(3,4,str(stamp))
sheet.update_cell(3,5,'Source: sunrise-sunset.org')
sheet.update_cell(4,5,'Called by: sunrise.py')
print('Sunrise data successfully loaded for',currentDt)