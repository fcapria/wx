#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Dark Sky calls

import requests, gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from wx_conversions import degrees2dir, meters2miles
from os import path
from open_api import openKey #Get API key at openweathermap.org
import mysql.connector
# Database secrets and config
from db_secrets import user, pwd, host
config = {
    'user': user,
    'password': pwd,
    'host': host,
    'database': 'Weather',
    'port': '3306'  # MySQL default port
}

MISS = 'Missing'

openwx = 'https://api.openweathermap.org/data/3.0/onecall?lat='
lat04849 = '44.4278389'
lon04849 = '&lon=-69.0088705'
units = '&units=imperial'
excludes = '&exclude=minutely,hourly,daily,alerts'
key = '&appid='+ openKey
filePath = path.abspath(__file__) # full path of this script
dirPath = path.dirname(filePath) # full path of the directory 
jsonFilePath = path.join(dirPath,'wx_secret.json') # absolute json file path

openCall = openwx + lat04849 + lon04849 + units + excludes + key

try:
    openData = requests.get(openCall)
    openJSON = openData.json()
    data = openJSON['current']
    #print(data)
    opened = True
except:
    print('JSON read error')
    opened = False

if opened:
    # Open DB connection and set cursor
    dbOpened = True
try:
    conn = mysql.connector.connect(**config)
except:
    print("Unable to connect to database")
    dbOpened = False
# Initialize the cursor and add a row to the db
if conn.is_connected():
    cursor = conn.cursor()
    sql = "INSERT INTO Wx (loc) VALUES ('04849');" 
    cursor.execute(sql)
    conn.commit()
    dbRow = cursor.lastrowid
try:
    colName = 'description'
    currentCond = data['weather'][0][colName]
    #currentCond = currentCond.replace(" ","_")
    #print("dbOpened = ",dbOpened)
    if dbOpened:
        sql = "UPDATE Wx SET description = %s WHERE ID = %s"
        values = (currentCond,dbRow)
        cursor.execute(sql,values)
        conn.commit()
except:
    currentCond = MISS
try:
    temp = str(round(data['temp'],1)) + "°F"
    if dbOpened:
        sql = "UPDATE Wx SET temp = %s WHERE ID = %s"
        values = (data['temp'],dbRow)
        cursor.execute(sql,values)
        conn.commit()
except:
    temp = MISS
try:
    dew = str(round(data['dew_point'],1)) + "°F"
    if dbOpened:
        sql = "UPDATE Wx SET dew_point = %s WHERE ID = %s"
        values = (data['dew_point'],dbRow)
        cursor.execute(sql,values)
        conn.commit()
except:
    dew = MISS
try:
    humid = str(data['humidity'])+'%'
    if dbOpened:
        sql = "UPDATE Wx SET humidity = %s WHERE ID = %s"
        values = (data['humidity'],dbRow)
        cursor.execute(sql,values)
        conn.commit()
except:
    humid = MISS
try:
    feels = str(round(data['feels_like'],1)) + "°F" 
    if dbOpened:
        sql = "UPDATE Wx SET feels_like = %s WHERE ID = %s"
        values = (data['feels_like'],dbRow)
        cursor.execute(sql,values)
        conn.commit()
except:
    feels = MISS
try:
    windDir = degrees2dir(data['wind_deg'])
    if dbOpened:
        sql = "UPDATE Wx SET wind_deg = %s WHERE ID = %s"
        values = (data['wind_deg'],dbRow)
        cursor.execute(sql,values)
        conn.commit()
except:
    windDir = MISS
try:
    windSpeed = str(round(data['wind_speed'],1)) + ' MPH'
    if dbOpened:
        sql = "UPDATE Wx SET wind_speed = %s WHERE ID = %s"
        values = (data['wind_speed'],dbRow)
        cursor.execute(sql,values)
        conn.commit()
except:
    windSpeed = MISSING
try:
    windGust = str(round(data['wind_gust'],1)) + ' MPH'
    if dbOpened:
        sql = "UPDATE Wx SET wind_gust = %s WHERE ID = %s"
        values = (data['wind_gust'],dbRow)
        cursor.execute(sql,values)
        conn.commit()
except:
    windGust = MISS
try:
    vis = meters2miles(data['visibility'])
    if dbOpened:
        sql = "UPDATE Wx SET visibility = %s WHERE ID = %s"
        values = (data['visibility'],dbRow)
        cursor.execute(sql,values)
        conn.commit()
except:
    vis = MISS

# A bunch of data not added to the Google Sheet, but worth storing
if dbOpened:
    sql = "UPDATE Wx SET pressure = %s WHERE ID = %s"
    values = (data['pressure'],dbRow)
    cursor.execute(sql,values)
    conn.commit()
    sql = "UPDATE Wx SET uvi = %s WHERE ID = %s"
    values = (data['uvi'],dbRow)
    cursor.execute(sql,values)
    conn.commit()
    sql = "UPDATE Wx SET clouds = %s WHERE ID = %s"
    values = (data['clouds'],dbRow)
    cursor.execute(sql,values)
    conn.commit()

# Close db connection
if conn.is_connected():
    cursor.close()
    conn.close()          

if opened:           
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(jsonFilePath, scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    
    try:
        sheet = client.open('wx04849').sheet1
    except gspread.exceptions.APIError as ex:
        print ("Sheet didn't open when called by darksky.py")
        print(ex)
    
    row = 9
    col = 2
    stamp = str(datetime.now())
    sheet.update_cell(row,4,stamp)
    sheet.update_cell(row,5,'Source: Open Weather')
    sheet.update_cell(row + 1,5,'Called by open2.py')
    sheet.update_cell(row,col,currentCond)
    row += 1
    sheet.update_cell(row,col,temp)
    row += 1
    sheet.update_cell(row,col,dew)
    row += 1
    sheet.update_cell(row,col,humid)
    row += 1
    sheet.update_cell(row,col,feels)
    row += 1
    sheet.update_cell(row,col,windDir)
    row += 1
    sheet.update_cell(row,col,windSpeed)
    row += 1
    sheet.update_cell(row,col,windGust)
    row += 1
    sheet.update_cell(row,col,vis)
    
else:
    print('Something went wrong. Server code {}'.format(data.status_code))
    

    # Open the database connection
    db = TinyDB('db.json')
    # Grab the current date and time separately as an integer
    rightNow = datetime.now()
    tm = int(rightNow.strftime("%H%M"))
    dt = int(rightNow.strftime("%Y%m%d"))
    
    # Add code here to only use top of the hour reading 
    # Or procrastinate and grab one reading per hour when calculating averages
    # Or procrasintate further and assume averages contain no duplicates 
    # and are good enough <-- CHOSEN

    # Use floating point temp reading
    db.insert({'date': dt, 'time': tm, 'temp': temp})

    print ('Successfully updated current weather ',stamp)