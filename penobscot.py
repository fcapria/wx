#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Penobscot buoy weather calls 

import gspread
from feedparser import parse
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from wx_conversions import toMi, toMph, firstWord, round_f

def mph(kn): # Converts knots to MPH
    speed = round((kn * 1.15),1)
    return speed

data = parse('https://www.ndbc.noaa.gov/data/latest_obs/44033.rss')
entries = data['entries'][0]
summary = entries['summary']
soup = BeautifulSoup(summary,'lxml')
items = soup.find_all('description')
cleanText = soup.get_text()

desc = cleanText.split('\n')
del(desc[0:2]) # remove date and location

readings = ['Wind Direction', 'Wind Speed', 'Wind Gust', 'Significant Wave Height',\
    'Dominant Wave Period', 'Atmospheric Pressure', 'Air Temperature', 'Water Temperature',\
    'Visibility']

mph = ['Wind Gust', 'Wind Speed']
mi = 'Visibility'

lengthy = ['Wind Direction', 'Atmospheric Pressure', 'Air Temperature', 'Water Temperature']
temps = [lengthy[2], lengthy[3]]

if len(desc) == 9:
    complete = True
else:
    complete = False
dataDict = {}
for i in range (0, len(desc)):
    temp = desc[i].split(': ')
    dataDict[temp[0]] = temp[1]

# Conversions to mph from knots 

for item in mph:
    try:
        temp = dataDict[item].split(' ')
        temp = toMph(float(temp[0]))
        dataDict[item] = temp
    except:
        pass 

# Conversion to miles from nmi

try:
    temp = dataDict['Visibility'].split(' ')
    temp = toMi(float(temp[0]))
    dataDict['Visibility'] = temp
except:
    pass 

# Stripping parentherticals, etc.
for item in lengthy:
    try:
        dataDict[item] = firstWord(dataDict[item])
    except:
        pass

try:
    dataDict['Atmospheric Pressure'] = dataDict['Atmospheric Pressure'] + ' in'
except:
    pass

for item in temps:
    try:
        dataDict[item] = round_f(dataDict[item])
    except:
        pass

# create a client to interact with Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('wx_secret.json', scope)
client = gspread.authorize(creds)

# Find workbook by name and open  first sheet

try:
    sheet = client.open('wx04849').sheet1
except:
    print ("Google Sheet didn't open for penobscot.py")

row = 19
col = 1

stamp = str(datetime.now())
sheet.update_cell(row,4,stamp)
sheet.update_cell(row,5,'Source: Penobscot Bay Buoy 44033')
sheet.update_cell(row+1,5,'Called by: penobscot.py')
for i in range(0,9): 
    sheet.update_cell(row,1,readings[i])
    try:
        sheet.update_cell(row,2,dataDict[readings[i]])
    except:
        sheet.update_cell(row,2,'Missing')
    row += 1

if complete:
    print('Complete nautical data retireved.')
else:
    print('Incomplete nautical data retrieved.')

