#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Penobscot buoy weather calls
# Upated 2024-01-05
# Downloads a text file via HTTPS, eliminating need for RSS parsing
# If data not available from Penobscot Bay, queries other buoys in the region

# Feb 19, 2024
# Added data storage to MySQL database for future data display and analysis

import gspread, urllib.request
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from wx_conversions import nm_to_mi, hpa_to_in, ms_to_mph      
from wx_conversions import compass, m_to_ft, c_to_f         
from os import path

# Database secrets and config
import mysql.connector
from db_secrets import user, pwd, host

buoyCols = ['YYYY','MM','DD','hh','mm','WDIR','WSPD','GST','WVHT','DPD','APD',
            'MWD','PRES','PTDY','ATMP','WTMP','DEWP','VIS','TIDE']
config = {
    'user': user,
    'password': pwd,
    'host': host,
    'database': 'Weather',
    'port': '3306'  # MySQL default port
}
dBaseUp = True
try:
    conn = mysql.connector.connect(**config)
except:
    print("Unable to connect to database")
    dBaseUp = False

if conn.is_connected():
    cursor = conn.cursor()
# Now ready to add data to database


def null_check(colContents):
    nullFlag = False
    if colContents == 'MM':
        nullFlag = True
    return(nullFlag)

def update(currentDict,row,col,lookup):
    nullFlagged = null_check(currentDict[lookup])
    if not nullFlagged:
        sql = "UPDATE Buoy_Data SET " + str(col) + " = " + str(currentDict[lookup]) + " WHERE ID = " + str(row)
        #values = (currentDict[col],row)
        cursor.execute(sql) 
        conn.commit()

# Inialize a dictionary to map column names in buoy data to column names in BuouyData db
colMap = {}
for col in buoyCols:
    if col != 'mm':
        colMap[col] = col
    else:
        colMap[col] = 'mn'

# buoyNames = {'44033':'Penobscot Bay','MSIM1':'Matinicus Rock','44032':'Central ME Shelf','44034':'Eastern ME Shelf'}

filePath = path.abspath(__file__) # full path of this script
dirPath = path.dirname(filePath) # full path of the directory 
jsonFilePath = path.join(dirPath,'wx_secret.json') # absolute json file path

STARTROW = 19
offset = 0

buoys = ['44033','MISM1','44032','44034']
error = False

try:
    with urllib.request.urlopen('https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt') as f:
        allData = f.read().decode("utf-8")
except:
    print('Failed to retrieve buoy data.')
    error = True

# Grab the column headers and place in a list
lines = allData.split('\n')
headers = lines[0].split()

stationsFound = 0
stationsData = []
# Iterate through data to grab the station data we want
for i in range(1,len(lines)-1):
    words = lines[i].split()
    if words[0] in buoys:
        stationsData.append(lines[i])
        stationsFound += 1

# Initialize the temp dictionaries 
penobscotDict = {}
penobscotDict['#STN'] = '44033'
for n in range (1,len(headers)):
    penobscotDict[headers[n]] = 'MM'
mantinicusDict = {}
mantinicusDict['#STN'] = 'M'
for n in range (1,len(headers)):
    mantinicusDict[headers[n]] = 'MM'
centralDict = {}
centralDict['#STN'] = '44032'
for n in range (1,len(headers)):
    centralDict[headers[n]] = 'MM'
easternDict = {}
easternDict['#STN'] = '44034'
for n in range (1,len(headers)):
    easternDict[headers[n]] = 'MM'

# Now fill the dictionaries with good data where available
for i in range (0,stationsFound):
    tempList = stationsData[i].split()
    if tempList[0] == '44032':
        for x in range (0,len(headers)-1):
            newKey = headers[x]
            newVal = tempList[x]
            centralDict[newKey] = newVal
        # Insert ROW for 44032 Buoys_Data
        sql = "INSERT INTO Buoy_Data (STN) VALUES (44032);" 
        cursor.execute(sql)
        conn.commit()
        dbRow = cursor.lastrowid
        for colName in buoyCols:
            dbCol = colMap[colName]
            update(centralDict,dbRow,dbCol,colName)
    elif tempList[0] == '44033':
        for x in range (0,len(headers)-1):
            newKey = headers[x]
            newVal = tempList[x]
            penobscotDict[newKey] = newVal
        if conn.is_connected:            
            cursor = conn.cursor()
            # Insert ROW for 44033 Buoys_Data
            sql = "INSERT INTO Buoy_Data (STN) VALUES (44033);" 
            cursor.execute(sql)
            conn.commit()
            dbRow = cursor.lastrowid
            for colName in buoyCols:
                dbCol = colMap[colName]
                update(penobscotDict,dbRow,dbCol,colName)
    elif tempList[0] == '44034':
        for x in range (0,len(headers)-1):
                newKey = headers[x]
                newVal = tempList[x]
                easternDict[newKey] = newVal
        # Insert ROW for 44034 Buoys_Data
        sql = "INSERT INTO Buoy_Data (STN) VALUES (44034);" 
        cursor.execute(sql)
        conn.commit()
        dbRow = cursor.lastrowid
        for colName in buoyCols:
            dbCol = colMap[colName]
            update(easternDict,dbRow,dbCol,colName)
    elif tempList[0] == 'MISM1':
        for x in range (0,len(headers)-1):
            newKey = headers[x]
            newVal = tempList[x]
            mantinicusDict[newKey] = newVal
        # Insert ROW for MISM1 Buoys_Data
        sql = "INSERT INTO Buoy_Data (STN) VALUES ('MISM1');" 
        cursor.execute(sql)
        conn.commit()
        dbRow = cursor.lastrowid
        for colName in buoyCols:
            dbCol = colMap[colName]
            update(mantinicusDict,dbRow,dbCol,colName)
# Create a master dictionary from Penobscot readings
masterDict = {}
for n in range (0,len(headers)):
    masterDict[headers[n]] = penobscotDict[headers[n]]
            
# Dictionary to store data sources of master dictionary
sourcesDict = {}
for n in range (0,len(headers)):
    sourcesDict[headers[n]] = 'Penobscot Bay'

# Replace missing information where possible
for item in headers:
    if masterDict[item] == 'MM':
        masterDict[item] = mantinicusDict[item]
        sourcesDict[item] = 'Mantinicus Rock'
for item in headers:
    if masterDict[item] == 'MM':
        masterDict[item] = centralDict[item]
        sourcesDict[item] = 'Central Shelf'
for item in headers:
    if masterDict[item] == 'MM':
        masterDict[item] = easternDict[item]
        sourcesDict[item] = 'Eastern Shelf'

# Lists for conversions needed
metersSec = ['WSPD','GST',] # meters per second to mph
centigrade = ['ATMP','WTMP',"DEWP"] # degrees c to f
nautical =  ['VIS'] #nautical miles to miles
meters = ['WVHT'] # meters to feet
hpa = ["PRES","PTDY"] # hPa to inches hg
direction = ["WDIR"] # convert from degrees to compass
sec = ["DPD","APD"] # seconds are not converted, 'sec' suffix added

for entry in masterDict:
    if entry in metersSec and masterDict[entry] != 'MM':
        masterDict[entry] = ms_to_mph(masterDict[entry])
    elif entry in centigrade and masterDict[entry] != 'MM':
        masterDict[entry] = c_to_f(masterDict[entry])
    elif entry in nautical and masterDict[entry] != 'MM':
        masterDict[entry] = nm_to_mi(masterDict[entry])
    elif entry in meters and masterDict[entry] != 'MM':
        masterDict[entry] = m_to_ft(masterDict[entry])
    elif entry in hpa and masterDict[entry] != 'MM':
        masterDict[entry] = hpa_to_in(masterDict[entry])
    elif entry in direction and masterDict[entry] != 'MM':
        masterDict[entry] = compass(masterDict[entry])
    elif entry in sec and masterDict[entry] != 'MM':
        masterDict[entry] = str(masterDict[entry] + ' sec')

# Change MM to Missing
for item in headers:
    if masterDict[item] == 'MM':
        masterDict[item] = 'Missing'

# Now write to the spreadsheet

# Create a client to interact with Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(jsonFilePath, scope)
client = gspread.authorize(creds)

# Find workbook by name and open the first sheet

try:
    sheet = client.open('wx04849').sheet1
except:
    print ("Google Sheet didn't open for penobscot3.py")
# Should stop if this error is raised. Also should be logged

row = STARTROW
col = 1
station = masterDict['#STN']

sheet.update_cell(row,5,station)
sheet.update_cell(row+1,5,'Called by: penobscot3.py')

# Enter the data into the sheet
param = 'WDIR'
sheet.update_cell(row,1,'Wind Direction')
sheet.update_cell(row,2,masterDict[param])
sheet.update_cell(row,4,sourcesDict[param])
row += 1
param = 'WSPD'
sheet.update_cell(row,1,'Wind Speed')
sheet.update_cell(row,2,masterDict[param])
sheet.update_cell(row,4,sourcesDict[param])
row += 1
param = 'GST'
sheet.update_cell(row,1,'Wind Gust')
sheet.update_cell(row,2,masterDict[param])
sheet.update_cell(row,4,sourcesDict[param])
row += 1
param ='WVHT'
sheet.update_cell(row,1,'Significant Wave Height')
sheet.update_cell(row,2,masterDict[param])
sheet.update_cell(row,4,sourcesDict[param])
row += 1
param = 'DPD'
sheet.update_cell(row,1,'Dominant Wave Period')
sheet.update_cell(row,2,masterDict[param])
sheet.update_cell(row,4,sourcesDict[param])
row += 1
param = 'PRES'
sheet.update_cell(row,1,'Atmospheric Pressure')
sheet.update_cell(row,2,masterDict[param])
sheet.update_cell(row,4,sourcesDict[param])
row += 1
param = 'ATMP'
sheet.update_cell(row,1,'Air Temperature')
sheet.update_cell(row,2,masterDict[param])
sheet.update_cell(row,4,sourcesDict[param])
row += 1
param = 'WTMP'
sheet.update_cell(row,1,'Water Temperature')
sheet.update_cell(row,2,masterDict[param])
sheet.update_cell(row,4,sourcesDict[param])
row += 1
param = 'VIS'
sheet.update_cell(row,1,'Visibility at Sea')
sheet.update_cell(row,2,masterDict[param])
sheet.update_cell(row,4,sourcesDict[param])
stamp = str(datetime.now())
sheet.update_cell(STARTROW-1,4,stamp)

# Close db connection
if conn.is_connected():
    cursor.close()
    conn.close()