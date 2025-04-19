#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime, requests, json, logging, pytz, gspread, ephem
from oauth2client.service_account import ServiceAccountCredentials
from wx_conversions import am_pm
from moon_api import apiKey
from os import path

def get_phase(year,month,day):

    """Returns a floating-point number from 0-1. where 0=new, 0.5=full, 1=new"""
    
    # Ephem stores its date numbers as floating points, which the following uses
    # to conveniently extract the percent time between one new moon and the next
    # This corresponds (somewhat roughly) to the phase of the moon.
    # Lifted from a tutorial. I would like to credit the author, but lost the link

    # Use Year, Month, Day as arguments
   
    date = ephem.Date(datetime.date(year,month,day))

    nnm = ephem.next_new_moon(date)
    pnm = ephem.previous_new_moon(date)

    lunation=(date-pnm)/(nnm-pnm)

    # There is a ephem.Moon().phase() command, but it can't differentiate 
    # between waxing and waning.

    return lunation

def definePhase(date):
    ephDate = ephem.Date(date)

    moonToday = ephem.Moon(ephDate)
    illumToday = moonToday.phase

    moonYesterday = ephem.Moon(ephDate - 1)  # One ephem day = 1 day
    illumYesterday = moonYesterday.phase

    waxing = illumToday > illumYesterday

    if illumToday < 1.0:
        return "New Moon"
    elif illumToday < 49.0:
        return "Waxing Crescent" if waxing else "Waning Crescent"
    elif 49.0 <= illumToday <= 51.0:
        return "First Quarter" if waxing else "Last Quarter"
    elif illumToday < 98.0:
        return "Waxing Gibbous" if waxing else "Waning Gibbous"
    else:
        return "Full Moon"
    
def main():
# BODY
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Set log file location
    
    logPath = path.join(path.dirname(path.abspath(__file__)), 'wx04849.log')

    logging.basicConfig(
        filename=logPath,
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    logging.info(">>> TEST: Logging system initialized <<<")

    logging.info("===== Starting moon.py =====")

    attempts = 0
    maxAttempts = 4
    response = None
    
    today = datetime.datetime.now()
    fullDt = today.strftime('%Y-%-m-%-d')
    yr, mo, dt = today.year, today.month, today.day

    base = 'https://api.ipgeolocation.io/astronomy?apiKey=' 
    # Define apiKey in moon_api.py and store in same directory as this script
    latLong = '&lat=44.308&long=-69.051'
    date = '&date=' + fullDt
    call = base + apiKey + latLong

    while attempts < maxAttempts: 
        try:
            response = requests.get(call, timeout=10)
            response.raise_for_status()
            logging.info(f"Successfully connected to ipgeolocation.com on attempt {attempts + 1}")
            break
        except requests.exceptions.RequestException:  
            attempts += 1
            logging.warning(f"Attempt {attempts} failed to reach ipgeolocation.com")
            logging.exception(ex)
            time.sleep(2 * attempts)  # backoff
    else:
        logging.error("All retry attempts to ipgeolocation failed")
    
    #Set absolute path
    filePath = path.abspath(__file__) # full path of this script
    dirPath = path.dirname(filePath) # full path of the directory 
    jsonFilePath = path.join(dirPath,'wx_secret.json') # absolute json file path    

    try:
        data = json.loads(response.text)
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(jsonFilePath, scope)
        client = gspread.authorize(creds)
        sheet = client.open('wx04849').sheet1
    except (json.JSONDecodeError, gspread.exceptions.APIError, Exception) as ex:
        logging.exception("Failed to initialize Google Sheet or parse API data")
    return  # exit early

    try:
        data = json.loads(response.text)
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(jsonFilePath, scope)
        client = gspread.authorize(creds)
        sheet = client.open('wx04849').sheet1
    except (json.JSONDecodeError, gspread.exceptions.APIError, Exception) as ex:
        logging.exception("Failed to initialize Google Sheet or parse API data")
    return  # exit early

    logging.info("===== Finished moon.py successfully =====")
    

if __name__ == "__main__":
    main()
