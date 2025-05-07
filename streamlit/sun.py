import streamlit as st
import requests
import json
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# === Load coordinates from config ===
with open("nbro_config.json") as f:
    config = json.load(f)

lat = config["latitude"]
lon = config["longitude"]

# === Fetch data from sunrise-sunset.org ===
url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0"
response = requests.get(url)
data = response.json()["results"]

sunrise_utc = datetime.fromisoformat(data["sunrise"].replace("Z", "+00:00"))
sunset_utc = datetime.fromisoformat(data["sunset"].replace("Z", "+00:00"))

# Convert to local time using zoneinfo (handles DST automatically)
eastern = ZoneInfo("America/New_York")
sunrise_local = sunrise_utc.astimezone(eastern)
sunset_local = sunset_utc.astimezone(eastern)

# Current time in Eastern
now = datetime.now(tz=eastern)

# Determine previous and next event dynamically
if now < sunrise_local:
    prev_event = ("Sunset (yesterday)", None)
    next_event = ("Sunrise", sunrise_local)
elif now < sunset_local:
    prev_event = ("Sunrise", sunrise_local)
    next_event = ("Sunset", sunset_local)
else:
    tomorrow_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date=tomorrow&formatted=0"
    tomorrow_data = requests.get(tomorrow_url).json()["results"]
    tomorrow_sunrise_utc = datetime.fromisoformat(tomorrow_data["sunrise"].replace("Z", "+00:00"))
    tomorrow_sunrise_local = tomorrow_sunrise_utc.astimezone(eastern)

    prev_event = ("Sunset", sunset_local)
    next_event = ("Sunrise (tomorrow)", tomorrow_sunrise_local)

# === Daylight duration ===
day_length = data["day_length"]
hours, remainder = divmod(int(day_length), 3600)
minutes = remainder // 60
length_str = f"{hours}h {minutes}m"

# === Prepare event time strings ===
prev_time_str = prev_event[1].strftime("%-I:%M %p") if prev_event[1] else "N/A"
next_time_str = next_event[1].strftime("%-I:%M %p")

# === Streamlit UI ===
st.set_page_config(page_title="Sunlight Info", layout="centered")

html_block = f"""
<div style='background-color: #f0f2f6; padding: 24px; border-radius: 12px;'>
    <div style='text-align: center; margin-bottom: 20px;'>
        <div style='font-size: 20px; font-weight: 600;'>{prev_event[0]}</div>
        <div style='font-size: 24px;'>{prev_time_str}</div>
    </div>
    <div style='text-align: center; margin-bottom: 20px;'>
        <div style='font-size: 20px; font-weight: 600;'>{next_event[0]}</div>
        <div style='font-size: 24px;'>{next_time_str}</div>
    </div>
    <div style='text-align: center;'>
        <div style='font-size: 20px; font-weight: 600;'>Daylight</div>
        <div style='font-size: 24px;'>{length_str}</div>
    </div>
</div>
"""

st.markdown(html_block, unsafe_allow_html=True)
