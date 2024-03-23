#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# LIBRARIES
import requests, json, calendar, gspread
from datetime import datetime, timedelta
from pytz import timezone
#from wxfunctions import solar
import iso8601 as iso 
from oauth2client.service_account import ServiceAccountCredentials
from os import path
from dateutil.parser import isoparse

# FUNCTIONS

def eastern(dt):
    dateObj = iso.parse_date(dt)
    #print(dateObj)
    dateEastern = dateObj.astimezone(timezone('America/New_York'))
    return(dateEastern)

def ampm (string):
    # Converts 24h time to 12h time
    timeList = string.split(':')
    hour = timeList[0]
    minute = timeList[1]
    second = timeList[2]    
    hour = int(hour)
    if hour == 0:
        hour = 12
        suffix = ' AM'
    elif hour < 12:
        suffix = ' AM'
    elif hour == 12:
        suffix = ' PM'
    else:
        hour = hour - 12
        suffix = ' PM'
    string = str(hour) + ':' + minute + ':' + second + suffix
    return string

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

def solar(latitude,longitude,dt):  
    base = 'https://api.sunrise-sunset.org/json'
    loc = '?lat=' + latitude + '&lng=' +longitude
    suffix = '&formatted=0&date=' 
    url = base + loc + suffix + dt 
    print(url)
    
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as ex:
        print(ex)
    
    allData = json.loads(response.text)
    results = allData['results']
    return(results)

# INITIALIZATIONS
error = False

# Get latitude and logitude from sheet

# BODY

# use absolute path to access credentials
filePath = path.abspath(__file__) # full path of this script
dirPath = path.dirname(filePath) # full path of the directory 
jsonFilePath = path.join(dirPath,'wx_secret.json') # absolute json file path

# Use stored credentials for client of the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(jsonFilePath, scope)
client = gspread.authorize(creds)

# Sheet shared with weatherman@weather04849.iam.gserviceaccount.com
# Find the workbook by name and open the first sheet
try:
    book = client.open('wx04849')
    sheet = book.worksheet('Sheet1')
except:
    print ('Google Sheet did not open.')
    error = True
"""
# Read cells containing lat and long
try:
        lat = sheet.range('A2')
        lat = str(lat[0])
        lon = sheet.range('B2')
        lon = str(lon[0])
except:
        error = True
"""
LAT = '44.279397'
LON = '-69.007578'


# Get the dates
todayDate = datetime.today().date()
yesterdayDate = todayDate - timedelta(days=1)
tomorrowDate = todayDate + timedelta(days=1)

try:
    data = solar(LAT,LON,str(todayDate))
except:
        error = True
        print('Error retrieving data from sunrise-sunset.org.')

sunriseIso = data['sunrise']
sunrise = eastern(sunriseIso)
sunrise = ampm(sunrise.strftime('%H:%M:%S'))

sunsetIso = data['sunset']
sunset = eastern(sunsetIso)
sunset = ampm(sunset.strftime('%H:%M:%S'))
print(sunset)   
dayLength = daylength(data['day_length'])

todaySec = int(data['day_length'])

sheet.update_cell(1,1,str(todayDate))
sheet.update_cell(3,2,sunrise)
sheet.update_cell(4,2,sunset)
sheet.update_cell(5,2,dayLength)

stamp = str(datetime.now())
sheet.update_cell(3,4,stamp)

# Close the Google session

try: 
    client.session.close()
except:
    print ('Session did not close properly')