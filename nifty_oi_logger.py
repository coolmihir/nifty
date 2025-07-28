import os
import json
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Step 1: Decode the base64 credentials
creds_b64 = os.environ["GOOGLE_CREDS_B64"]
creds_json = base64.b64decode(creds_b64).decode("utf-8")
creds_dict = json.loads(creds_json)

# Step 2: Authorize gspread using the credentials dictionary
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
