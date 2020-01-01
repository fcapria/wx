#!/usr/bin/python3
# -*- coding: utf-8 -*-

# This script is designed to be run every 15 minutes to update today's data
# and archive the readings.

# Yesterday's data is only updated if it has not been archived and the day 
# is complete.

import json, gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials 
from datetime import datetime
from tinydb import TinyDB, Query, where
from statistics import mean
from wx_conversions import today_int, yesterday_int

def up_to_date(yesterday):
    archive = TinyDB('archive.json')
    current = False
    Date = Query()
    result = archive.search(Date.date == yesterday)
    if len(result) > 0:
        current = True
    archive.close()
    return current

def calc_yesterday(yesterday):
    db = TinyDB('db.json')
    temps = []
    Date = Query()
    result = db.search(Date.date == yesterday)
    
    for item in result:
        temps.append(item['temp'])
    db.close()
    yesterHigh = round(max(temps),1)
    yesterLow = round(min(temps),1)
    yesterAvg = round(mean(temps),1)
    archive = TinyDB('archive.json')    
    archive.insert({'date': yesterday, 'high': yesterHigh, 'low': yesterLow, 'avg': yesterAvg})

def make_str(n):
    suffix = '°F'
    n = str(n) + suffix
    return n

# Get today's date as an integer
currently = datetime.now()
today = today_int()
yesterday = yesterday_int()

current = up_to_date(yesterday)
if not current:
    calc_yesterday(yesterday)

# Query for temps from today and yesterday and load into lists
db = TinyDB("db.json")
todayTemps = []
for item in db:
    if item['date'] == today:
        todayTemps.append(item['temp'])

# Calculate high, low and average for today
# Mean is from statistics
# Min and max are built into Python

todayHigh = round(max(todayTemps),1)
todayLow = round(min(todayTemps),1)
todayAvg = round(mean(todayTemps),1)

# Publish today's data only

# Use credentials to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('wx_secret.json', scope)
client = gspread.authorize(creds)

# Access workbook by name and open the appropriate tab

try:
    sheet = client.open('wx04849').get_worksheet(1)
    # 1 is the index value of Sheet2
    # Google doesn't document how to access Sheet2
    # See https://stackoverflow.com/questions/33570749/python-gspread-library-only-writes-to-worksheet-labeled-sheet1
except:
    print ("Sheet didn't open when called by yesterday.py")

sheet.update_cell(6,2,make_str(todayHigh))
sheet.update_cell(7,2,make_str(todayLow))
sheet.update_cell(8,2,make_str(todayAvg))

stamp = str(datetime.now())
sheet.update_cell(6,3,stamp)

print("Today's high, low and averages updated.")