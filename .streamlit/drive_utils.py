#!/usr/bin/env python3
"""
drive_utils.py – Upload generated files to a Google Drive folder using
OAuth user credentials (i.e. uploading *as you*, the folder owner).

Why OAuth and not a service account?
    A service account has no storage quota of its own, so it cannot own
    files in a personal (non-Workspace) Google Drive — uploads fail with
    `storageQuotaExceeded`. Uploading with the owner's OAuth credentials
    stores files against the owner's quota, which works on personal Gmail.

Setup (one time):
    1. Create an OAuth client (type: Desktop app) in Google Cloud and set
       the OAuth consent screen publishing status to **In production**
       (otherwise the refresh token expires after 7 days).
    2. Run `python generate_token.py` locally to consent once and obtain a
       refresh token.
    3. Put client_id, client_secret and refresh_token into Streamlit
       secrets under [google_oauth] (see .streamlit/secrets.toml.example).

The destination folder ID is parsed from the link you provided:
    https://drive.google.com/drive/folders/1M53kFacEkHVE8UTU3j4jqOFLJxWVD7Cp
"""

from __future__ import annotations

import mimetypes
from typing import Optional

# Destination folder, parsed from the shared link.
DEFAULT_FOLDER_ID = "1M53kFacEkHVE8UTU3j4jqOFLJxWVD7Cp"

# Full drive scope so the app can write into an existing folder you own.
SCOPES = ["https://www.googleapis.com/auth/drive"]

TOKEN_URI = "https://oauth2.googleapis.com/token"


class DriveError(RuntimeError):
    """Raised when an upload cannot be completed."""


def _build_service(oauth_info: dict):
    """Build an authenticated Drive v3 client from OAuth user credentials."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError as e:  # pragma: no cover - depends on deploy env
        raise DriveError(
            "Google API libraries are not installed. Add "
            "'google-api-python-client' and 'google-auth' to requirements.txt."
        ) from e

    missing = [k for k in ("client_id", "client_secret", "refresh_token")
               if not oauth_info.get(k)]
    if missing:
        raise DriveError(
            "Missing OAuth credential field(s): " + ", ".join(missing)
            + ". Check the [google_oauth] block in Streamlit secrets."
        )

    creds = Credentials(
        token=None,
        refresh_token=oauth_info["refresh_token"],
        client_id=oauth_info["client_id"],
        client_secret=oauth_info["client_secret"],
        token_uri=TOKEN_URI,
        scopes=SCOPES,
    )

    try:
        creds.refresh(Request())
    except Exception as e:
        raise DriveError(
            "Could not refresh Google credentials. The refresh token has "
            "likely expired or been revoked. Re-run generate_token.py to "
            "create a new one, and make sure the OAuth consent screen is set "
            f"to 'In production' (Testing tokens expire after 7 days). ({e})"
        ) from e

    return build("drive", "v3", credentials=creds, cache_discovery=False)


def upload_file(
    file_path: str,
    file_name: str,
    oauth_info: dict,
    folder_id: str = DEFAULT_FOLDER_ID,
    mime_type: Optional[str] = None,
) -> dict:
    """
    Upload a single local file into the Drive folder, as the OAuth user.

    Returns a dict with the new file's 'id', 'name', and 'webViewLink'.
    Raises DriveError on any failure.
    """
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError

    if mime_type is None:
        mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    service = _build_service(oauth_info)

    metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    try:
        created = (
            service.files()
            .create(
                body=metadata,
                media_body=media,
                fields="id, name, webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )
    except HttpError as e:
        status = getattr(getattr(e, "resp", None), "status", "?")

        reason, detail = "", ""
        try:
            import json as _json
            payload = _json.loads(e.content.decode("utf-8"))
            err = payload.get("error", {})
            detail = err.get("message", "")
            errs = err.get("errors", [])
            if errs:
                reason = errs[0].get("reason", "")
        except Exception:
            pass

        if reason == "storageQuotaExceeded" or "storage quota" in detail.lower():
            raise DriveError(
                "Storage quota exceeded for the account that authorized this "
                f"upload. (Google: {detail or reason})"
            ) from e
        if reason == "accessNotConfigured":
            raise DriveError(
                "The Google Drive API is not enabled for this project. "
                "Enable it under APIs & Services -> Library, then retry. "
                f"(Google: {detail or reason})"
            ) from e
        if str(status) == "404":
            raise DriveError(
                f"Folder '{folder_id}' not found, or the authorized account "
                "does not have access to it. Confirm the folder ID and that "
                f"you signed in as an account that can edit it. (Google: {detail or reason})"
            ) from e
        if str(status) in ("401", "403"):
            raise DriveError(
                "Permission denied"
                + (f" ({reason})" if reason else "")
                + ". Confirm the authorized account can edit this folder and "
                f"the Drive API is enabled. (Google: {detail})"
            ) from e
        raise DriveError(f"Drive upload failed (HTTP {status}): {detail or e}") from e
    except Exception as e:
        raise DriveError(f"Drive upload failed: {e}") from e

    return created
