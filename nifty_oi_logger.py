import os
import json
import base64
import time
import gspread
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Step 1: Decode Google credentials from Railway env variable
print("🔐 Decoding credentials from GOOGLE_CREDS_B64...")
creds_b64 = os.environ.get("GOOGLE_CREDS_B64")
if not creds_b64:
    raise Exception("❌ GOOGLE_CREDS_B64 not found in environment variables!")

creds_json = base64.b64decode(creds_b64).decode("utf-8")
creds_dict = json.loads(creds_json)

# Step 2: Authenticate with Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
print("✅ Google Sheets authentication successful.")

# Step 3: Open Google Sheet using its ID
try:
    sheet_id = "1POEQcuFy37AY0exoSxWPtAgcYAy8xZUNQidJ5A-5T_k"  # <- your actual sheet
    sheet = client.open_by_key(sheet_id).sheet1
    print("📄 Opened Google Sheet successfully.")
except Exception as e:
    print("❌ Failed to open Google Sheet:", str(e))
    raise e

# Step 4: Fetch NSE data using ScraperAPI
print("🌐 Sending NSE request via ScraperAPI...")

SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
if not SCRAPER_API_KEY:
    raise Exception("❌ SCRAPER_API_KEY not found in environment variables!")

nse_url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
scraper_url = f"https://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={nse_url}"

try:
    res = requests.get(scraper_url, timeout=15)
    print("🌐 ScraperAPI Response Code:", res.status_code)
    data = res.json()
except Exception as e:
    print("❌ Failed to fetch NSE data via ScraperAPI:", str(e))
    raise e

# Step 5: Process and append to Google Sheet
try:
    records = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item in data["records"]["data"]:
        if "CE" in item and "PE" in item:
            strike = item["strikePrice"]
            ce_oi = item["CE"]["openInterest"]
            ce_chg = item["CE"]["changeinOpenInterest"]
            pe_oi = item["PE"]["openInterest"]
            pe_chg = item["PE"]["changeinOpenInterest"]
            underlying = item["CE"]["underlyingValue"]
            row = [timestamp, strike, ce_oi, ce_chg, pe_oi, pe_chg, underlying]
            records.append(row)

    print(f"🧾 Prepared {len(records)} rows to log.")

    for row in records:
        sheet.append_row(row)
        print("📤 Row added to sheet:", row)

except Exception as e:
    print("❌ Error during data processing or sheet update:", str(e))
    raise e

# Step 6: Exit cleanly
print("✅ Script completed and exited cleanly.")
time.sleep(3)
