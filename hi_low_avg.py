#!/usr/bin/python3
# -*- coding: utf-8 -*-

# This script is designed to be run every 15 minutes to update today's data
# and archive the readings.

# Yesterday's data is only updated if needed

import json, gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials 
from datetime import datetime
from tinydb import TinyDB, Query, where
from statistics import mean
from wx_conversions import today_int, yesterday_int

ERR = 'No Data'
SUFFIX = '°F'

def up_to_date(yesterday):
    archive = TinyDB('archive.json')
    current = False
    dt = Query()
    result = archive.search(dt.date == yesterday)
    if len(result) > 0:
        current = True
    archive.close()
    return current

def calc_yesterday(yesterday):
    db = TinyDB('db.json')
    temps = []
    dt = Query()
    result = db.search(dt.date == yesterday)
    if len(result) > 0:
        for item in result:
            temps.append(item['temp'])
        db.close()
        yHigh = round(max(temps),1)
        yLow = round(min(temps),1)
        yAvg = round(mean(temps),1)
        archive = TinyDB('archive.json')    
        archive.insert({'date': yesterday, 'high': yHigh, 'low': yLow, 'avg': yAvg})
    else:
        yHigh = ERR
        yLow = ERR
        yAvg = ERR
    return yHigh, yLow, yAvg

def make_str(n):
    if n != ERR:
        n = str(n) + SUFFIX
    return n

# Get today's date as an integer
currently = datetime.now()
today = today_int()
yesterday = yesterday_int()

# Use credentials to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('wx_secret.json', scope)
client = gspread.authorize(creds)

# Access workbook by name and open the appropriate tab
sheetErr = False
try:
    sheet = client.open('wx04849').get_worksheet(1)
   
    # 1 is the index value of Sheet2
    # Google doesn't document how to access Sheet2
    # https://stackoverflow.com/questions/33570749/python-gspread-library-only-writes-to-worksheet-labeled-sheet1
except gspread.exceptions.APIError as ex:
    print(ex)
    print ("Sheet didn't open when called by hi_low_avg.py")
    sheetErr = True
stamp = str(datetime.now()) # Timestamp for updates

if not up_to_date(yesterday):
    try:
        yesterdayResults = calc_yesterday(yesterday)
        sheet.update_cell(2,2,make_str(yesterdayResults[0]))
        sheet.update_cell(3,2,make_str(yesterdayResults[1]))
        sheet.update_cell(4,2,make_str(yesterdayResults[2]))
        sheet.update_cell(2,3,stamp)
        print("passed")
        print(yesterdayResults[0],yesterdayResults[1],yesterdayResults[2])
    except AttributeError as ex:
        sheet.update_cell(2,2,'ERR')
        sheet.update_cell(3,2,'ERR')
        sheet.update_cell(4,2,'ERR')
        sheet.update_cell(2,3,stamp)
        print(ex)

# Query for temps from today and load into list
db = TinyDB('db.json')
todayTemps = []
for item in db:
    if item['date'] == today:
        todayTemps.append(item['temp'])

# Calculate high, low and average for today
# Mean is from statistics
# Min and max are built into Python

if not sheetErr:
    try:
        todayHigh = round(max(todayTemps),1)
        todayLow = round(min(todayTemps),1)
        todayAvg = round(mean(todayTemps),1)
        sheet.update_cell(6,2,make_str(todayHigh))
        sheet.update_cell(7,2,make_str(todayLow))
        sheet.update_cell(8,2,make_str(todayAvg))
    except ValueError as ex:
        sheet.update_cell(6,2,ERR)
        sheet.update_cell(7,2,ERR)
        sheet.update_cell(8,2,ERR)
        
    # Publish today's data only
        
    sheet.update_cell(6,3,stamp)
    print("Today's high, low and averages updated.")
    print(db)
else:
    print('Databased not updated ',stamp)