
import requests
import json
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("NIFTY_OI_Logger").sheet1  # Rename as needed

# Fetch NSE OI data
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
}
session.headers.update(headers)
session.get("https://www.nseindia.com")

url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
res = session.get(url)

if res.status_code == 200:
    data = res.json()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records = data['records']['data']
    underlying = data['records'].get('underlyingValue', 'NA')

    for item in records:
        strike = item.get("strikePrice", "NA")
        ce_oi = item.get("CE", {}).get("openInterest", "")
        ce_chg = item.get("CE", {}).get("changeinOpenInterest", "")
        pe_oi = item.get("PE", {}).get("openInterest", "")
        pe_chg = item.get("PE", {}).get("changeinOpenInterest", "")

        row = [timestamp, strike, ce_oi, ce_chg, pe_oi, pe_chg, underlying]
        sheet.append_row(row)
    print("✅ Data logged successfully at", timestamp)
else:
    print("❌ Failed to fetch data:", res.status_code)
