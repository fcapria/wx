#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Standalone test script of function logic for alt_temp 
To be added to wx_conversions and called by penobscot.py
February 1, 2020
"""


import requests, time, urllib.request
from bs4 import BeautifulSoup

url = ' https://www.seatemperature.org/north-america/united-states/camden.htm'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
data = soup.find('div', id='sea-temperature')
data = str(data).split(' / ')
data = str(data[1]).split('\n')
print(data[0])
