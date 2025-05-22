#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# LIBRARIES
import requests, json, calendar, gspread
from datetime import datetime, timedelta
from pytz import timezone
import iso8601 as iso 
from oauth2client.service_account import ServiceAccountCredentials
from os import path
from dateutil.parser import isoparse

# FUNCTIONS
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
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as ex:
        print(ex)
    
    allData = json.loads(response.text)
    results = allData['results']
    return(results)

def eastern(dt):
    dateObj = iso.parse_date(dt)
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
    # Accounts for 0 hours because function also used to calculate difference in day length
    if hours > 0:
        durationStr = f"{hours} hours, {minutes} minutes, {seconds} seconds"
    else:
        durationStr = f"{minutes} minutes, {seconds} seconds"
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

# INITIALIZATIONS
error = False

# Get latitude and logitude from sheet

# BODY
beginning = datetime.now()

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
    book = client.open('wx01532')
    sheet = book.worksheet('Sheet1')
except:
    print ('Google Sheet did not open.')
    error = True

# Read cells containing lat and long
try:
        lat = sheet.range('A2')
        lat = str(lat[0])
        lon = sheet.range('B2')
        lon = str(lon[0])
        meLat = sheet.range('A10')
        meLat = str(meLat[0])
        meLon = sheet.range('B10')
        meLon = str(meLon[0])
except:
        error = True

# Store dates
todayDate = datetime.today().date()
yesterdayDate = todayDate - timedelta(days=1)
tomorrowDate = todayDate + timedelta(days=1)

if not error:
    lat = lat.split("'")[1] 
    lon = lon.split("'")[1]
    meLat = meLat.split("'")[1]
    meLon = meLon.split("'")[1]
    try:
        data = solar(lat,lon,str(todayDate))
    except:
         error = True
         print('Error getting today MA from sunrise-sunset.org.')
    try:
        meData = solar(meLat,meLon,str(todayDate))
    except:
         error = True
         print('Error getting today ME from sunrise-sunset.org.')
    try:
        yesterdayData = solar(lat,lon,str(yesterdayDate))
        meYesterday = solar(meLat,meLon,str(yesterdayDate))
        tomorrowData = solar(lat,lon,str(tomorrowDate))
        meTomorrow = solar(meLat,meLon,str(tomorrowDate))
    except:
         error = True
         print('Error retrieving yesterday and tomorrow data from sunrise-sunset.org.')

difference = int(meData['day_length']) - int(data['day_length'])

if difference <= 0:
    MALonger = True
else:
    MALonger = False

diffStr = daylength(abs(difference)) + ' more daylight'

sunriseIso = data['sunrise']
yesterdaySunriseIso = yesterdayData['sunrise']
tomorrowSunriseIso = tomorrowData['sunrise']
sunrise = eastern(sunriseIso)
yesterdaySunrise = eastern(yesterdaySunriseIso)
tomorrowSunrise = eastern(tomorrowSunriseIso)
sunrise = ampm(sunrise.strftime('%H:%M:%S'))
yesterdaySunrise = ampm(yesterdaySunrise.strftime('%H:%M:%S'))
tomorrowSunrise = ampm(tomorrowSunrise.strftime('%H:%M:%S'))

sunriseIso = data['sunrise']
meSunriseIso = meData['sunrise']
yesterdaySunriseIso = yesterdayData['sunrise']
meYesterdayRiseIso = meYesterday['sunrise']
tomorrowSunriseIso = tomorrowData['sunrise']
meTomorrowRiseIso = meTomorrow['sunrise']
sunrise = eastern(sunriseIso)
meSunrise = eastern(meTomorrowRiseIso)
yesterdaySunrise = eastern(yesterdaySunriseIso)
meYesterdayRise = eastern(meYesterdayRiseIso)
tomorrowSunrise = eastern(tomorrowSunriseIso)
meTomorrowRise = eastern(meTomorrowRiseIso)
sunrise = ampm(sunrise.strftime('%H:%M:%S'))
meSunrise = ampm(meSunrise.strftime('%H:%M:%S'))
yesterdaySunrise = ampm(yesterdaySunrise.strftime('%H:%M:%S'))
meYesterdayRise = ampm(meYesterdayRise.strftime('%H:%M:%S'))
tomorrowSunrise = ampm(tomorrowSunrise.strftime('%H:%M:%S'))
meTomorrowRise = ampm(meTomorrowRise.strftime('%H:%M:%S'))

sunsetIso = data['sunset']
meSunsetIso = meData['sunset']
yesterdaySunsetIso = yesterdayData['sunset']
meYesterdaySetIso = meYesterday['sunset']
tomorrowSunsetIso = tomorrowData['sunset']
meTomorrowSetIso = meTomorrow['sunset']
sunset = eastern(sunsetIso)
meSunset = eastern(meSunsetIso)
yesterdaySunset = eastern(yesterdaySunsetIso)
meYesterdaySet = eastern(meYesterdaySetIso)
tomorrowSunset = eastern(tomorrowSunsetIso)
meTomorrowSet = eastern(meTomorrowSetIso)
sunset = ampm(sunset.strftime('%H:%M:%S'))
meSunset = ampm(meSunset.strftime('%H:%M:%S'))
yesterdaySunset = ampm(yesterdaySunset.strftime('%H:%M:%S'))
meYesterdaySet = ampm(meYesterdaySet.strftime('%H:%M:%S'))
tomorrowSunset = ampm(tomorrowSunset.strftime('%H:%M:%S'))
meTomorrowSet = ampm(meTomorrowSet.strftime('%H:%M:%S'))
dayLength = daylength(data['day_length'])
meDayLen = daylength(meData['day_length'])
yesterdayLength = daylength(yesterdayData['day_length'])
meYesterdayLen = daylength(meYesterday['day_length'])
tomorrowlength = daylength(tomorrowData['day_length'])
meTomorrowLen = daylength(meTomorrow['day_length'])

todaySec = int(data['day_length'])
meTodaySec = int(meData['day_length'])
yesterdaySec = int(yesterdayData['day_length'])
meYesterdaySec = int(meYesterday['day_length'])
tomorrowSec = int(tomorrowData['day_length'])
meTomorrowSec = int(meTomorrow['day_length'])

yesterdayDelta = int(yesterdaySec - todaySec)
meYesDelta =int(meYesterdaySec - meTodaySec)
yesterdayDeltaStr = mmssdelta(yesterdayDelta)
meYesDeltaStr = mmssdelta(meYesDelta)

tomorrowDelta = int(tomorrowSec - todaySec)
meTomDelta = int(meTomorrowSec - meTodaySec)
tomorrowDeltaStr = mmssdelta(tomorrowDelta)
meTomDeltaStr = mmssdelta(meTomDelta)
sheet.update_cell(3,3,' ')
sheet.update_cell(11,3,' ')


if MALonger:
    sheet.update_cell(3,3,diffStr)
else:
    sheet.update_cell(11,3,diffStr)
#sheet.update_cell(5,1,str(todayDate))
#sheet.update_cell(13,1,str(todayDate))
sheet.update_cell(5,2,sunrise)
sheet.update_cell(13,2,meSunrise)
sheet.update_cell(5,3,sunset)
sheet.update_cell(13,3,meSunset)
sheet.update_cell(5,4,dayLength)
sheet.update_cell(13,4,meDayLen)
#sheet.update_cell(6,1,str(yesterdayDate))
#sheet.update_cell(14,1,str(yesterdayDate))
sheet.update_cell(6,2,yesterdaySunrise)
sheet.update_cell(14,2,meYesterdayRise)
sheet.update_cell(6,3,yesterdaySunset)
sheet.update_cell(14,3,meYesterdaySet)
sheet.update_cell(6,4,yesterdayLength)
sheet.update_cell(14,4,meYesterdayLen)
sheet.update_cell(14,5,meYesDeltaStr)
sheet.update_cell(6,5,yesterdayDeltaStr)
#sheet.update_cell(7,1,str(tomorrowDate))
#sheet.update_cell(15,1,str(tomorrowDate))
sheet.update_cell(7,2,tomorrowSunrise)
sheet.update_cell(15,2,meTomorrowRise)
sheet.update_cell(7,3,tomorrowSunset)
sheet.update_cell(15,3,meTomorrowSet)
sheet.update_cell(7,4,tomorrowlength)
sheet.update_cell(15,4,meTomorrowLen)
sheet.update_cell(7,5,tomorrowDeltaStr)
sheet.update_cell(15,5,meTomDeltaStr)

# Add time stamp
now = datetime.now() 
stamp = "Updated " + now.strftime('%Y-%m-%d %H:%M')
sheet.update_cell(16,1,stamp)
start = "Started - " + beginning.strftime('%Y-%m-%d %H:%M:%S')

sheet.update_cell(17,1,start)
ending = datetime.now()
end = "Ended - " + ending.strftime('%Y-%m-%d %H:%M:%S')
sheet.update_cell(18,1,end)

# Close the Google session
try: 
    client.session.close()
except:
    print ('Session did not close properly')