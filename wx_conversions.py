#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def toMph(kn):
    # conversion from knots to mph
    mph = kn * 1.151
    mph = str(int(round(mph,0))) + ' mph'
    return mph

def ms_to_mph(ms):
    # Conversion from meters per second to mph
    # Added March 2022
    try:
        mph = float(ms)*2.23694
        mph = (str(float(round(mph,1)))) + ' mph'
    except:
        mph = "Error"
    return mph

def toMi(nmi):
    # conversion from nautical miles to miles
    # Added March 2022
    mi = nmi * 1.151
    mi = str(round(mi,1)) + ' miles'
    return(mi)

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

def firstWord(string):
    # Only the first word is preserved
    string = string.split(' ')
    string = string[0]
    return string

def round_f(fTemp):
    # rounds a value to an integer then converts it ot a string
    temp = fTemp.split('°')
    temp = temp[0]
    temp = round(float(temp),0)
    temp = int(temp)
    fTemp = str(temp + '°F')
    return fTemp

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
    import requests, json
    base = 'https://api.sunrise-sunset.org/json?'
    time = '&formatted=0'
    url = base + loc + time
    
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as ex:
        logging.exception("Request to sunrise-sunset API failed")
    
    allData = json.loads(response.text)
    results = allData['results']   
    return(results)

# Function to scrape a web page for data
# Feb 1, 2020

def alt_temp(): 
    import requests
    from bs4 import BeautifulSoup
    data = []

    url = 'https://www.seatemperature.org/north-america/united-states/camden.htm'
    response = requests.get(url)

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.find('div', id='sea-temperature')
        print(soup)
        print('*********')
        print(data)
        print('*******')
        data = str(data).split(' / ')
        data = str(data[1]).split('\n')
    except:
        data[0] = 'Missing'
    return data[0]    
    
def load_bouy():
    # Added March 2022
    BOUY = "44033"
    SECOND = "MISM1"

    station = ' '

    import urllib.request

    try:
        with urllib.request.urlopen('https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt') as f:
            allData = f.read().decode("utf-8")
    except:
        print('failed to retrieve data')
    print(f)
    buoyData = {}   
    allRows = allData.split('\n')
    entries = allRows[0].split(' ')
    entries = list(filter(None,entries))
    primaryFound = False
    secondaryFound = False
    for dataRow in allRows:
        readings = dataRow.split(" ")
        if readings[0] == BOUY:
            usableData = list(filter(None,readings))
            primaryFound = True
            station = 'Penobscot Bay 44033'
            continue
    if not primaryFound:
        for dataRow in allRows:
            readings = dataRow.split(" ")
            if readings[0] == SECOND:
                usableData = list(filter(None,readings))
                secondaryFound = True
                station = 'Matinicus Rock MISM1'
                continue
    if primaryFound or secondaryFound:
        for i in range (0, len(entries)):
            buoyData[entries[i]] = usableData[i]
    else:
        for i in range (0, len(entries)):
            buoyData[entries[i]] = 'MM'
    
    buoyData[entries[0]] = station

    print(station)
    print('*******')
    print(buoyData[entries[0]])
    print('*******')
    
    return(buoyData)

def hpa2inches(hpa):
    hpa = float(hpa)
    inches = (round(hpa * 0.02953,2))
    return(str(inches) + ' in.')
           
def meters2miles(meters):
    meters = float(meters)
    mi = str(round(meters * 0.000621371,1)) + ' mi.'
    return(mi)
    

    
    