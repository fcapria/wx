#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# January 1, 2020
# Frank Capria 

"""
Yesterday's high, low and average temperatures

This script is designed to be run every day shortly after midnight. 
If it fails to run, hi_low_avg.py will catch the error next time it runs
The intent is to update yesterday data only as needed.

"""
import gspread
from tinydb import TinyDB, Query
from oauth2client.service_account import ServiceAccountCredentials 
from wx_conversions import today_int, yesterday_int
from datetime import datetime

# Open db and pull yesterday's data

# Archive contains high, low and average
# Date is stored as integer YYYYMMDD
# Pull max, min and mean from archive

yesterday = yesterday_int()
archive = TinyDB('archive.json')
Date = Query()
result = archive.search(Date.date == yesterday)
result = result[0] # Pulls data out of list format 

# Open the sheet

# Use credentials to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('wx_secret.json', scope)
client = gspread.authorize(creds)

# Access workbook by name and open the appropriate tab

try:
    sheet = client.open('wx04849').get_worksheet(1)
    # 1 is the index value of Sheet2
    # Google doesn't document this
    # See https://stackoverflow.com/questions/33570749/python-gspread-library-only-writes-to-worksheet-labeled-sheet1
except:
    print ("Sheet didn't open when called by yesterday.py")

suffix = '°F'
highStr = str(result['high']) + suffix
lowStr = str(result['low']) + suffix
avgStr = str(result['avg']) + suffix
# Write to Google Sheet
sheet.update_cell(2,2,highStr)
sheet.update_cell(3,2,lowStr)
sheet.update_cell(4,2,avgStr)

stamp = str(datetime.now())
sheet.update_cell(2,3,stamp)

print("Yesterday's values updated.")