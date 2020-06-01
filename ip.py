#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Frank Capria
May 18, 2020
Store the public IP address
"""

import gspread
from requests import get
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

ip = get('https://api.ipify.org').text
print(ip)

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('wx_secret.json', scope)
client = gspread.authorize(creds)

ok = True

try:
    sheet = client.open('recent04849').sheet1
except gspread.exceptions.APIError as ex:
    print ('Google Sheet did not open.', ex)
    ok = False

if ok:
    sheet.update_acell('b3',ip)
    stamp = str(datetime.now())
    sheet.update_acell('c3',stamp)
    print(stamp)


