import os
import json
import base64
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime

# Step 1: Load credentials from Railway environment variable
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

# Step 3: Open the target Google Sheet
try:
    sheet = client.open("NIFTY_OI_Logger").sheet1  # Make sure this sheet is shared with your service account!
    print("📄 Opened Google Sheet: NIFTY_OI_Logger")
except Exception as e:
    print("❌ Failed to open Google Sheet:", str(e))
    raise e

# Step 4: Fetch data from NSE
url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

print("🌐 Sending request to NSE API...")
session = requests.Session()
session.headers.update(headers)

try:
    res = session.get(url, timeout=10)
    print("🌐 NSE API Response Code:", res.status_code)
    data = res.json()
except Exception as e:
    print("❌ Failed to fetch NSE data:", str(e))
    raise e

# Step 5: Process and log data
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

    print(f"🧾 Prepared {len(records)} rows for logging.")

    for row in records:
        sheet.append_row(row)
        print("📤 Row added to sheet:", row)

except Exception as e:
    print("❌ Error while processing or appending data:", str(e))
    raise e

# Final confirmation
print("✅ Script completed and exited cleanly.")
time.sleep(3)
