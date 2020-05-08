#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Frank Capria
April 18, 2020
Based on sunrise.py 
github.com/fcapria/wx
"""

from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from wx_conversions import getSun
 
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
secDif = str((lengthMe - lengthMa) % 60)
difString = str(minDif + ' min ' + secDif + ' sec')

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
sheet.update_cell(34,5,'Daily by comp.py')

print('Updated daylight comparison ',str(stamp))