#!/usr/bin/env python3
"""
generate_token.py - Run this ONCE on your own computer to authorize the
app and obtain a refresh token for uploading to your Google Drive.

Prerequisites:
    pip install google-auth-oauthlib
    A downloaded OAuth client file named 'client_secret.json' in this folder
    (Google Cloud -> APIs & Services -> Credentials -> Create credentials ->
    OAuth client ID -> Application type: Desktop app -> download JSON).

Usage:
    python generate_token.py

A browser window opens; sign in with the Google account that owns the
destination Drive folder and approve access. The script then prints a
ready-to-paste [google_oauth] block for your Streamlit secrets.
"""

import json
import sys
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/drive"]
CLIENT_FILE = "client_secret.json"


def main() -> int:
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Missing dependency. Run:  pip install google-auth-oauthlib")
        return 1

    if not Path(CLIENT_FILE).exists():
        print(f"'{CLIENT_FILE}' not found in this folder.")
        print("Download it from Google Cloud Console -> Credentials -> "
              "OAuth client ID (Desktop app), rename to client_secret.json, "
              "and place it next to this script.")
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
    # Opens a browser, runs a tiny local server to catch the redirect.
    creds = flow.run_local_server(port=0, prompt="consent")

    if not creds.refresh_token:
        print("No refresh token was returned. Remove this app's access at "
              "https://myaccount.google.com/permissions and run again.")
        return 1

    with open(CLIENT_FILE) as f:
        data = json.load(f)
    info = data.get("installed") or data.get("web") or {}
    client_id = info.get("client_id", creds.client_id)
    client_secret = info.get("client_secret", creds.client_secret)

    print("\n" + "=" * 60)
    print("Success. Paste this into your Streamlit secrets:")
    print("=" * 60 + "\n")
    print("[google_oauth]")
    print(f'client_id = "{client_id}"')
    print(f'client_secret = "{client_secret}"')
    print(f'refresh_token = "{creds.refresh_token}"')
    print("\n(Keep these private - do not commit them to git.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
