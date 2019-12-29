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

nbroLoc = '42.3305976,-71.6352203'
lincLoc = '/44.4278389,-69.0088705' 
excludes = '?exclude=flags,minutely,hourly,daily'
darkCall = darkSky + APIkey + lincLoc + excludes
done = False
count = 0
while not done and (count < 4):
    data = requests.get(darkCall)

    if data.ok:
        dataJSON = data.json()
        wx = dataJSON['currently']
        summary = wx['summary']
        temp = int(round(wx['temperature'],0))
        tempFl = float(wx['temperature'])
        temp = str(temp) + '°F'
        dewPt = str(int(round(wx['dewPoint'],0))) + '°F'
        humidity = str(int(round(wx['humidity'] * 100,0))) + '%'
        feelsLike = str(int(round(wx['apparentTemperature'],0))) + '°F'
        direction = wx['windBearing']
        compass = degrees2dir(direction)
        roundSpeed = int(round(wx['windSpeed'],0))
        speed = str(roundSpeed) + ' mph'
        roundGust = int(round(wx['windGust'],0))
        gusts = str(roundGust) + ' mph'
        visibility = round(wx['visibility'],1)
        visibility = str(visibility) + ' mi'
        #ozone = wx['ozone']    
        done = True
    else:
        time.sleep(120)
        count += 1

if done:         
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('wx_secret.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    
    try:
        sheet = client.open('wx04849').sheet1
    except:
        print ("Sheet didn't open when called by darksky.py")
    
    row = 9
    col = 2
    stamp = str(datetime.now())
    sheet.update_cell(row,4,stamp)
    sheet.update_cell(row,5,'Source: Dark Sky')
    sheet.update_cell(row + 1,5,'Called by darksky.py')
    sheet.update_cell(row,col,summary)
    row += 1
    sheet.update_cell(row,col,temp)
    row += 1
    sheet.update_cell(row,col,dewPt)
    row += 1
    sheet.update_cell(row,col,humidity)
    row += 1
    sheet.update_cell(row,col,feelsLike)
    row += 1
    sheet.update_cell(row,col,compass)
    row += 1
    sheet.update_cell(row,col,speed)
    row += 1
    sheet.update_cell(row,col,gusts)
    row += 1
    sheet.update_cell(row,col,visibility)

    # Open the database connection
    db = TinyDB('db.json')
    # Grab the current date and time separately as an integer
    rightNow = datetime.now()
    tm = int(rightNow.strftime("%H%M"))
    dt = int(rightNow.strftime("%Y%m%d"))
    # Add code here to only use top of the hour reading 
    # Or procrastinate and grab one reading per hour when calculating averages
    # Or procrasintate further and assume averafges contain no duplicates 
    #   and are good enough <-- CHOSEN

    # Use floating point temp reading
    db.insert({'date': dt, 'time': tm, 'temp': tempFl})

    print ('Successfully updated current weather ',stamp)
    
else:
    print('Something went wrong. Server code {}'.format(data.status_code))