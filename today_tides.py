#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat, Nov 2 13:34:09 2018
Revised November 30, 2019 to update Google Sheet as cron job
Revised December 27, 2019 to clean up display
Revised January 25, 2020 to list the tides for the day lessen script frequency

Frank Capria
"""
import urllib, json, time, pytz, gspread, requests
# import html.parser, gspread, requests
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
# from time_string import am_pm
from wx_conversions import round_f, am_pm, today_int
from os import path

def convert2ticks(s):
    # Lifted from the web
    return time.mktime(datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timetuple())

def clear(row):
    col=1
    sheet.update_cell(row,col,' ')
    sheet.update_cell(row,col+1,' ')

def cleanTime(string):
    temp = string.split(' ')
    string = am_pm(temp[1])
    return(string)

def round_1(n):
    n = round(float(n),1)
    n = str(n)
    return n

def get_row_data(di):
    tideType = di.get('type')
    if tideType == 'L':
        tideType = 'Low tide of '
    else:
        tideType = 'High tide of '
    tideHt = di.get('v') + ' ft'
    return (tideType + tideHt)
    
STARTROW = 29
    
station = str(8415490) #-- Rockland, ME 
name = 'Frank.Capria'  # Leave quotes

# Current date in YYYYMMDD format for call in format
# 48 hours ending on March 17, 2012 is --> end_date=20120307&range=48


currentDate = datetime.today().strftime('%Y%m%d')
values = []
sets = []
baseURL = 'https://tidesandcurrents.noaa.gov/api/'
queries = 'datagetter?product=predictions'
personalize ='&application=' + name +'&begin_date=' + currentDate + '&range=36&datum=MLLW&station='
formats = '&time_zone=lst_ldt&units=english&interval=hilo&format=JSON'
APIcall = baseURL + queries + personalize + station + formats

tides = urllib.request.urlopen(APIcall).read()
strResponse = tides.decode('utf-8')
data = json.loads(strResponse)
values = data.get('predictions')
now = time.time()

today = today_int()

j = len(values)

for i in range( j - 1, -1, -1): 
    di = values[i]
    tideEvent = values[i].get('t')
    t = datetime.strptime(tideEvent, "%Y-%m-%d %H:%M")
    tideDate = int(datetime.strftime(t, '%Y%m%d')) 
    if tideDate != today:
        values.pop(i)
        
# Now the list is culled to only today's tides. 
# It's possible there are only 3 tide events in a day
# Also the data might not be up to date
# Best to run script twice a day and clear four rows of old data

# create a client to interact with Google Drive API
# Instructions for getting credentials to update Google Sheet at:
# https://towardsdatascience.com/accessing-google-spreadsheet-data-using-python-90a5bc214fd2
# Create your own wx_secret.json file

#Set absolute path
filePath = path.abspath(__file__) # full path of this script
dirPath = path.dirname(filePath) # full path of the directory 
jsonFilePath = path.join(dirPath,'wx_secret.json') # absolute json file path    


if len(values) > 0: #Only run if we have data

    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(jsonFilePath, scope)
    client = gspread.authorize(creds)

    try:
        sheet = client.open('wx04849').sheet1 
    except:
        print ('Sheet did not open when called by daily_tides.py')
          
    for rowNum in range(STARTROW,STARTROW+4):
        clear(rowNum)
    
    dataRow = STARTROW
    for i in range (0,len(values)):
        col1 = get_row_data(values[i])
        col2 = cleanTime(values[i].get('t'))
        sheet.update_cell(dataRow,1,col1)
        sheet.update_cell(dataRow,2,col2)
        dataRow += 1

    stamp = str(datetime.now())
    sheet.update_cell(STARTROW,4,stamp)
    sheet.update_cell(STARTROW,5,'Source: Rockland Sta 8415490')
    sheet.update_cell(STARTROW+1,5,'Called by: today_tides.py')   
    print('Tide data updated successfully')



