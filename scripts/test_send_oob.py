"""Test script: call Firebase REST sendOobCode to request a password reset email.
This script loads .env, reads FIREBASE_WEB_API_KEY, and posts to the REST endpoint.
"""
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("FIREBASE_WEB_API_KEY")
email = "siivatmika0206@gmail.com"

if not api_key:
    print("ERROR: FIREBASE_WEB_API_KEY not set in environment.")
    raise SystemExit(1)

url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
payload = json.dumps({"requestType": "PASSWORD_RESET", "email": email}).encode("utf-8")
req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode('utf-8')
        print("HTTP_STATUS:", resp.status)
        print("RESPONSE_BODY:", body)
        print("RESULT: Request accepted by Firebase; check inbox/spam for the reset email.")
except urllib.error.HTTPError as he:
    try:
        err = he.read().decode('utf-8')
    except Exception:
        err = str(he)
    print("HTTP_ERROR_CODE:", he.code)
    print("HTTP_ERROR_BODY:", err)
    print("RESULT: Firebase returned an error; see above.")
except Exception as e:
    print("EXCEPTION:", str(e))
    print("RESULT: Network or other error occurred.")
