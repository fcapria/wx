# wx
🌤️ Weather and Astronomical Logger
A set of customizable Python scripts designed to collect real-time weather and astronomical data from public APIs and store the results in a Google Sheet.

✅ Features
Fetches current weather conditions, sunrise/sunset data, moon phase info, and buoy observations

Logs from multiple geographic locations

Writes results to a single Google Sheet for convenient tracking

Includes support for OpenWeather, Sunrise-Sunset.org, ipgeolocation.io, and NOAA Buoy Data Center

Modular design allows easy extension or customization

🔧 Setup
Clone this repo

Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Google Sheets Access

Create a Google Cloud project

Enable the Google Sheets API and Google Drive API

Download the service account JSON key file

Rename it wx_secret.json and store it in the project directory

API Keys

Some scripts require keys for the following:

OpenWeatherMap

ipgeolocation.io

Keys are stored in open_api.py or moon_api.py (not included—create locally)

Latitude & Longitude Config

Each location’s coordinates are stored in small JSON config files like:

json
Copy
Edit
{
  "latitude": "44.31",
  "longitude": "-69.05"
}
These can be customized or duplicated for other regions.

🗓️ Current Scripts

Script	Purpose
compare_daylight_temp.py	Compares daylight length and temperature between two locations
moon.py	Retrieves moon phase and illumination
today_tides.py	Gets tide data for a specific buoy or station
open2.py	Logs current conditions from OpenWeather API
penobscot3.py	Aggregates data from several NOAA buoy stations
🗂️ Deprecated: comp.py and compare.py have been replaced by compare_daylight_temp.py

📌 Notes
All APIs used are free to access but may require registration and key management

Google Sheets integration requires sharing your sheet with the service account email

Designed for cron jobs, Raspberry Pi, or light server-based automation

🧼 To Do
Merge more scripts into unified modules

Add tests and automated error notifications

Streamlit dashboard for web-based display