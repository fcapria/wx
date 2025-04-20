#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat, Nov 2 13:34:09 2018
Revised November 30, 2019 to update Google Sheet as cron job
Revised December 27, 2019 to clean up display
Revised January 25, 2020 to list the tides for the day lessen script frequency
Refactored April 19, 2025

Frank Capria
"""
import json, time, logging, pytz, gspread, requests
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from wx_conversions import round_f, am_pm, today_int
from os import path

def convert2ticks(s):
    # Lifted from the web
    return time.mktime(datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timetuple())

def clear(sheet,row):
    col=1
    sheet.update_cell(row,col,' ')
    sheet.update_cell(row,col+1,' ')

def cleanTime(string):
    temp = string.split(' ')
    string = am_pm(temp[1])
    return(string)

def round_1(n):
    n = round(float(n),1)
    n = str(n)
    return n

def getRowData(di):
    tideType = di.get('type')
    if tideType == 'L':
        tideType = 'Low tide of '
    else:
        tideType = 'High tide of '
    tideHt = di.get('v') + ' ft'
    return (tideType + tideHt)

def get_sheet() -> gspread.Worksheet:
    scriptDir = path.dirname(path.abspath(__file__))
    jsonPath = path.join(scriptDir, "wx_secret.json")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(jsonPath, scope)
    client = gspread.authorize(creds)

    try:
        return client.open('wx04849').sheet1
    except Exception as e:
        raise RuntimeError(f"Failed to open sheet: {e}")
    
def filterTodayTides(rawTides: list) -> list:
    today = today_int()
    filtered = []

    for tide in rawTides:
        tideTime = datetime.strptime(tide["t"], "%Y-%m-%d %H:%M")
        if int(tideTime.strftime('%Y%m%d')) == today:
            filtered.append(tide)
    
    return filtered

def main():

    logging.basicConfig(
        filename='wx04849.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )

    logging.info("===== Starting today_tides.py =====")

    STARTROW = 29
        
    station = str(8415490) #-- Rockland, ME 
    name = 'Frank.Capria'  # Leave quotes

    # Current date in YYYYMMDD format for call in format
    # 48 hours ending on March 17, 2012 is --> end_date=20120307&range=48


    currentDate = datetime.today().strftime('%Y%m%d')
    values = []
    baseURL = 'https://tidesandcurrents.noaa.gov/api/'
    queries = 'datagetter?product=predictions'
    personalize ='&application=' + name +'&begin_date=' + currentDate + '&range=36&datum=MLLW&station='
    formats = '&time_zone=lst_ldt&units=english&interval=hilo&format=JSON'
    APIcall = baseURL + queries + personalize + station + formats

    try:
        response = requests.get(APIcall)
        response.raise_for_status()  # Raises an HTTPError for bad status
        data = response.json()
        values = data.get('predictions', [])
        logging.info(f"Fetched {len(values)} tide from NOAA API.")
    except requests.RequestException as e:
        logging.error(f"Failed to fetch tide data: {e}")
        values = []

    values = data.get('predictions')

    values = filterTodayTides(values)
    logging.info(f"{len(values)} tide events remain after filtering for today.")
            
    # Now the list is culled to only today's tides. 
    # It's possible there are only 3 tide events in a day
    # Also the data might not be up to date
    # Best to run script twice a day and clear four rows of old data

    # create a client to interact with Google Drive API
    # Instructions for getting credentials to update Google Sheet at:
    # https://towardsdatascience.com/accessing-google-spreadsheet-data-using-python-90a5bc214fd2
    # Create your own wx_secret.json file

    if not values:
        logging.warning("No tide events found for today. Exiting without updating sheet.")

    if len(values) > 0: #Only run if we have data
        try:
            sheet = get_sheet()
    
        except:
            print ('Sheet did not open when called by daily_tides.py')
            
        for rowNum in range(STARTROW,STARTROW+4):
            clear(sheet,rowNum)
        
        dataRow = STARTROW
        rows = []
        for tide in values:
            col1 = getRowData(tide)
            col2 = cleanTime(tide.get('t'))
            rows.append([col1, col2])

        logging.info(f"Updating Google Sheet with {len(rows)} tide rows at A{STARTROW}.")

        sheet.update(
            range_name=f"A{STARTROW}:B{STARTROW + len(rows) - 1}",
            values=rows
        )

        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata = [
            [stamp, "Source: Rockland Sta 8415490"],
            ["", "Called by: today_tides.py"]
        ]

        sheet.update(
            range_name=f"D{STARTROW}:E{STARTROW + 1}",
            values=metadata
        )
        logging.info("Updated timestamp and metadata fields.")
        logging.info("Script:today_tides completed")

if __name__ == "__main__":
    main()