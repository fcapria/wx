#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat, Nov 2 13:34:09 2018
Revised November 30, 2019 to update Google Sheet as cron job
Revised December 27, 2019 to clean up display
Frank Capria
"""
import urllib, json, time, pytz, gspread, requests
#import html.parser, gspread, requests
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from time_string import am_pm
from wx_conversions import round_f

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
    
station = 8415490 #-- Rockland, ME 
name = 'Frank.Capria'  # Leave quotes

# Current date in YYYYMMDD format for call in format
# 48 hours ending on March 17, 2012 is --> end_date=20120307&range=48

currentDate = datetime.today().strftime('%Y%m%d')
values = []
sets = []
baseURL = 'https://tidesandcurrents.noaa.gov/api/'
queries = 'datagetter?product=predictions'
personalize ='&application=' + name +'&begin_date=' + currentDate + '&range=48&datum=MLLW&station='
formats = '&time_zone=lst_ldt&units=english&interval=hilo&format=JSON'
APIcall = baseURL + queries + personalize + str(station) + formats

tides = urllib.request.urlopen(APIcall).read()
strResponse = tides.decode('utf-8')
data = json.loads(strResponse)
values = data.get('predictions')
# print(values)
now = time.time()
j = len(values)

# create a client to interact with Google Drive API
# Instructions for getting credentials to update Google Sheet at:
# https://towardsdatascience.com/accessing-google-spreadsheet-data-using-python-90a5bc214fd2
# Create your own wx_secret.json file
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('wx_secret.json', scope)
client = gspread.authorize(creds)

try:
    sheet = client.open('wx04849').sheet1 
except:
    print ('Sheet did not open when called by tidal.py')

# clear existing data
row = 29
clear(row)
clear(row+1)

stamp = str(datetime.now())
sheet.update_cell(row,4,stamp)

for i in range (0,j):
    tideEvent = values[i].get('t')
    t = datetime.strptime(tideEvent, "%Y-%m-%d %H:%M")
    tide = time.mktime(datetime.strptime(tideEvent, \
                    "%Y-%m-%d %H:%M").timetuple())

    if tide >= now:
        tideGood = True
        nextEvent = values[i].get('type')
        first2 = values[i].get('t')
        first2 = cleanTime(first2)
        if nextEvent == 'L':
            first1 = 'Next low tide of ' + round_1(values[i].get('v')) + ' ft'
            sheet.update_cell(row,1,first1)
            sheet.update_cell(row,2,first2)
            try:
                second1 = 'Next high tide of ' + round_1(values[i+1].get('v')) + ' ft'
                second2 = cleanTime(values[i+1].get('t'))
                sheet.update_cell(row + 1,1,second1)
                sheet.update_cell(row + 1,2,second2)
            except:
                second1 = 'Prev. high tide of ' + round_1(values[i-1].get('v')) + ' ft'
                second2 = cleanTime(values[i-1].get('t'))
                sheet.update_cell(row + 1,1,second1)
                sheet.update_cell(row + 1,2,second2)
        else:
            first1 = 'Next high tide of ' + round_1(values[i].get('v')) + ' ft'
            sheet.update_cell(row,1,first1)
            sheet.update_cell(row,2,first2)
            try:
                second1 = 'Next low tide of ' + round_1(values[i+1].get('v')) + ' ft'
                second2 = cleanTime(values[i+1].get('t'))
                sheet.update_cell(row + 1,1,second1)
                sheet.update_cell(row + 1,2,second2)
            except:
                second1 = 'Prev. low tide of ' + round_1(values[i-1].get('v')) + ' ft'
                second2 = cleanTime(values[i-1].get('t'))
                sheet.update_cell(row + 1,1,second1)
                sheet.update_cell(row + 1,2,second2)
        break
    elif i == (j - 1):
        sheet.update_cell(row,1,'Tide data unavailable')
        break
sheet.update_cell(row,5,'Source: Rockland Sta 8415490')
sheet.update_cell(row+1,5,'Called by: tidal.py')   
print('Tide data updated successfully')





