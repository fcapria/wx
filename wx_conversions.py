#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests, json

# Both functions a string, not a float or int
# Ready for insertion into Sheet cell

def compass(d):
    # Converts degrees to compass setting
    # Should remove degrees2dir call
    # Added March 2022

    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    try:
        index = int(d) % 360
        index = round(float(index)/22.5,0)
        index = int(index)
        direction = dirs[index]
    except:
        direction = 'Missing'
    return direction

def nm_to_mi(nm):
    # Converts nautical miles to miles
    # Added March 2022
    try:
        mi = str(round(float(nm)*1.15078,1)) + " mi"
    except:
        mi = "Missing"
    return mi

def hpa_to_in(h):
    # Added March 2022
    inch = round(float(h)/33.864,1)
    inch = str(inch) + '"'
    return inch

def c_to_f(c):
    # Added March 2022
    try:
        f = round((float(c)*9/5)+32,1)
        f = str(f) + "°F"
    except:
        f = "Error"
    return f

def m_to_ft(m):
    # Added March 2022
    try:
        ft = round(float(m)*3.28084,1)
        ft = str(ft) + ' ft'
    except:
        ft = "Error"
    return ft

def ms_to_mph(ms):
    # Conversion from meters per second to mph
    # Added March 2022
    try:
        mph = float(ms)*2.23694
        mph = (str(float(round(mph,1)))) + ' mph'
    except:
        mph = "Error"
    return mph

def degrees2dir(d):
    # Highly approximate but good enough for now
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = int((d + 11.25)/22.5)
    return dirs[ix % 16]

def am_pm (string):
    # Converts 24h time to 12h time
    timeList = string.split(':')
    hour = timeList[0]
    minute = timeList[1]
    hour = int(hour)
    if hour == 0:
        hour = 12
        suffix = 'AM'
    elif hour < 12:
        suffix = 'AM'
    elif hour == 12:
        suffix = 'PM'
    else:
        hour = hour - 12
        suffix = 'PM'
    string = str(hour) + ':' + minute + ' ' + suffix
    return string

def today_int():
    from datetime import datetime
    currently = datetime.now()
    today = int(currently.strftime('%Y%m%d'))
    return today

def yesterday_int():
    from datetime import datetime, timedelta
    yesterday = int(datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d'))
    return yesterday

def getSun(loc):  
    
    # Migrated April 25, 2020
    base = 'https://api.sunrise-sunset.org/json?'
    time = '&formatted=0'
    url = base + loc + time

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        logging.exception("Request to sunrise-sunset API failed")
        raise

    allData = json.loads(response.text)
    results = allData['results']   
    return(results)

def meters2miles(meters):
    meters = float(meters)
    mi = str(round(meters * 0.000621371,1)) + ' mi.'
    return(mi)
    

    
    