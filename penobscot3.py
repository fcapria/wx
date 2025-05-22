import gspread, urllib.request, sys, logging
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from wx_conversions import nm_to_mi, hpa_to_in, ms_to_mph      
from wx_conversions import compass, m_to_ft, c_to_f         
from os import path
from wx_util import initLogging 

STARTROW = 19
BUOYS = ['44033','MISM1','44032','44034']

def initDict(station, headers):
    return {'#STN': station, **{key: 'MM' for key in headers[1:]}}

def display_source(source):
    return "" if source == "Penobscot Bay" else source

def main():
    initLogging("penobscot3.py")

    filePath = path.abspath(__file__)
    dirPath = path.dirname(filePath)
    jsonFilePath = path.join(dirPath,'wx_secret.json')

    try:
        with urllib.request.urlopen('https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt') as f:
            allData = f.read().decode("utf-8")
    except Exception as e:
        logging.exception("Failed to retrieve buoy data.")
        sys.exit(1)

    lines = allData.split('\n')
    headers = lines[0].split()

    penobscotDict = initDict('44033', headers)
    mantinicusDict = initDict('MISM1', headers)
    centralDict = initDict('44032', headers)
    easternDict = initDict('44034', headers)

    stationsData = []
    for line in lines[1:]:
        parts = line.strip().split()
        if not parts:
            continue
        if parts[0] in BUOYS:
            stationsData.append(line)
    logging.info(f"Found {len(stationsData)} matching buoy stations.")


    for line in stationsData:
        tempList = line.split()
        station = tempList[0]
        targetDict = {
            '44032': centralDict,
            '44033': penobscotDict,
            '44034': easternDict,
            'MISM1': mantinicusDict
        }.get(station)
        if targetDict:
            for i in range(1, len(headers)):
                targetDict[headers[i]] = tempList[i]

    masterDict = dict(penobscotDict)
    sourcesDict = {key: 'Penobscot Bay' for key in headers}

    for fallbackDict, source in [(mantinicusDict, 'Mantinicus Rock'), (centralDict, 'Central Shelf'), (easternDict, 'Eastern Shelf')]:
        for key in headers:
            if masterDict.get(key) == 'MM':
                masterDict[key] = fallbackDict.get(key)
                sourcesDict[key] = source

    conversions = {
        'WSPD': ms_to_mph, 'GST': ms_to_mph,
        'ATMP': c_to_f, 'WTMP': c_to_f, 'DEWP': c_to_f,
        'VIS': nm_to_mi,
        'WVHT': m_to_ft,
        'PRES': hpa_to_in, 'PTDY': hpa_to_in,
        'WDIR': compass,
    }
    secSuffix = {'DPD', 'APD'}

    for key, value in masterDict.items():
        if value != 'MM':
            if key in conversions:
                masterDict[key] = conversions[key](value)
            elif key in secSuffix:
                masterDict[key] = f"{value} sec"

    for key in headers:
        if masterDict[key] == 'MM':
            masterDict[key] = 'Missing'

    try:
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(jsonFilePath, scope)
        client = gspread.authorize(creds)
        sheet = client.open('wx04849').sheet1
    except Exception as e:
        logging.exception("Google Sheet didn't open for penobscot3.py")
        sys.exit(1)

    dataRows = [
            ['Wind Direction', masterDict['WDIR'], '', display_source(sourcesDict['WDIR'])],
            ['Wind Speed', masterDict['WSPD'], '', display_source(sourcesDict['WSPD'])],
            ['Wind Gust', masterDict['GST'], '', display_source(sourcesDict['GST'])],
            ['Significant Wave Height', masterDict['WVHT'], '', display_source(sourcesDict['WVHT'])],
            ['Dominant Wave Period', masterDict['DPD'], '', display_source(sourcesDict['DPD'])],
            ['Atmospheric Pressure', masterDict['PRES'], '', display_source(sourcesDict['PRES'])],
            ['Air Temperature', masterDict['ATMP'], '', display_source(sourcesDict['ATMP'])],
            ['Water Temperature', masterDict['WTMP'], '', display_source(sourcesDict['WTMP'])],
            ['Visibility at Sea', masterDict['VIS'], '', display_source(sourcesDict['VIS'])]
        ]
    """
    # Original
    sheet.update(range_name=f"A{STARTROW}:D{STARTROW + len(dataRows) - 1}", values=dataRows)
    sheet.update(range_name=f"D{STARTROW - 1}", values=[[str(datetime.now())]])
    sheet.update(range_name=f"E{STARTROW + 1}", values=[["Called by: penobscot3.py"]])
 
    # First update
    sheet.update(range_name=f"A{STARTROW}:D{STARTROW + len(dataRows) - 1}", values=dataRows)      
    sheet.update(range_name=f"D{STARTROW - 1}", values=[[str(datetime.now())]])                   
    sheet.update(range_name=f"E{STARTROW}", values=[["Penobscot Bay buoy data unless noted"]])    
    sheet.update(range_name=f"E{STARTROW + 1}", values=[["Called by: penobscot3.py"]])            
    """
    # Second update 
    sheet.batch_update([
        {
            "range": f"A{STARTROW}:D{STARTROW + len(dataRows) - 1}",
            "values": dataRows
        },
        {
            "range": f"D{STARTROW - 1}",
            "values": [[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]
        },
        {
            "range": f"E{STARTROW}",
            "values": [["Penobscot Bay buoy data unless noted"]]
        },
        {
            "range": f"E{STARTROW + 1}",
            "values": [["Called by: penobscot3.py"]]
        }
    ])

    logging.info("===== penobscot3.py completed successfully. =====")

if __name__ == "__main__":
    main()
