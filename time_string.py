#!/usr/bin/python3
# -*- coding: utf-8 -*-

# This file is obsolete. It's functions have been added to wx_conversions.py

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
