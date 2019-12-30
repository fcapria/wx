#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json, time
from datetime import datetime
from tinydb import TinyDB, Query, where
from statistics import mean

def up_to_date(yesterday):
    archive = TinyDB('archive.json')
    current = False
    Date = Query()
    result = archive.search(Date.date == yesterday)
    if len(result) > 0:
        current = True
    archive.close()
    print(current)
    return current

def calc_yesterday(yesterday):
    print('Entered calc_yesterday')
    db = TinyDB('db.json')
    temps = []
    Date = Query()
    result = db.search(Date.date == yesterday)
    for item in result:
        temps.append(item['temp'])
    print(temps)
    db.close()
    high = round(max(temps),1)
    low = round(min(temps),1)
    avg = round(mean(temps),1)
    archive = TinyDB('archive.json')    
    archive.insert({'date': yesterday, 'high': high, 'low': low, 'avg': avg})

# Get today's date as an integer
currently = datetime.now()
today = int(currently.strftime('%Y%m%d'))
yesterday = today - 1

current = up_to_date(yesterday)
if not current:
    calc_yesterday(yesterday)

# Query for temps from today and yesterday and load into lists
db = TinyDB("db.json")
yesterdayTemps = []
todayTemps = []
for item in db:
    if item['date'] == today:
        todayTemps.append(item['temp'])
    elif item['date'] == yesterday:
        yesterdayTemps.append(item['temp'])

# Calculate high, low and average for each day
# Mean is from statistics
# Min and max are built into Python

todayHigh = round(max(todayTemps),1)
todayLow = round(min(todayTemps),1)
todayAvg = round(mean(todayTemps),1)
print('Today')
print(todayHigh, todayLow, todayAvg)

archive = TinyDB('archive.json')
Date = Query()
result = archive.search(Date.date == yesterday)
# There can only be one entry per date
print('Yesterday')
print(result[0]['high'],result[0]['low'],result[0]['avg'])

# Publish them somewhere