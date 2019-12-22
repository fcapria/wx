#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Both functions a string, not a float or int
# Ready for insertion into Sheet cell

def toMph(kn):
    mph = kn * 1.151
    mph = str(int(round(mph,0))) + ' MPH'
    return mph

def toMi(nmi):
    mi = nmi *1.151
    mi = str(int(round(mi,0))) + ' MPH'
    return(mi)

def degrees2dir(d):
    # This is highly approximate but good enough for now
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = int((d + 11.25)/22.5)
    return dirs[ix % 16]

def am_pm (string):
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