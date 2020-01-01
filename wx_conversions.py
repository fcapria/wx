#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Both functions a string, not a float or int
# Ready for insertion into Sheet cell

def toMph(kn):
    # conversion from knots to mph
    mph = kn * 1.151
    mph = str(int(round(mph,0))) + ' mph'
    return mph

def toMi(nmi):
    # conversion from nautical miles to miles
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
    