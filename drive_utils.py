#!/usr/bin/env python3
"""
drive_utils.py – Upload generated files to a Google Drive folder.

A deployed Streamlit app cannot write to a Drive folder from just a
"shared link" — Google's API requires authenticated credentials. The
reliable, headless way to do this (no per-user login pop-up) is a
**service account**:

    1. Create a service account in Google Cloud Console and download its
       JSON key.
    2. Share the target Drive folder with the service account's email
       (the `client_email` in the JSON), giving it *Editor* access.
    3. Put the JSON under Streamlit secrets as `gcp_service_account`
       (see .streamlit/secrets.toml.example).

The destination folder ID is taken from the link you provided:
    https://drive.google.com/drive/folders/1M53kFacEkHVE8UTU3j4jqOFLJxWVD7Cp
"""

from __future__ import annotations

import mimetypes
from typing import Optional

# Destination folder, parsed from the shared link.
DEFAULT_FOLDER_ID = "1M53kFacEkHVE8UTU3j4jqOFLJxWVD7Cp"

# OAuth scope: drive.file only grants access to files this app creates,
# which is the least-privilege option and enough to upload here.
_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


class DriveError(RuntimeError):
    """Raised when an upload cannot be completed."""


def _build_service(service_account_info: dict):
    """Build an authenticated Drive v3 client from a service-account dict."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as e:  # pragma: no cover - depends on deploy env
        raise DriveError(
            "Google API libraries are not installed. Add "
            "'google-api-python-client' and 'google-auth' to requirements.txt."
        ) from e

    try:
        creds = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=_SCOPES
        )
    except Exception as e:
        raise DriveError(f"Invalid service-account credentials: {e}") from e

    # cache_discovery=False avoids a noisy warning on read-only filesystems.
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def upload_file(
    file_path: str,
    file_name: str,
    service_account_info: dict,
    folder_id: str = DEFAULT_FOLDER_ID,
    mime_type: Optional[str] = None,
) -> dict:
    """
    Upload a single local file into the Drive folder.

    Returns a dict with the new file's 'id', 'name', and 'webViewLink'.
    Raises DriveError on any failure.
    """
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError

    if mime_type is None:
        mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    service = _build_service(service_account_info)

    metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    try:
        created = (
            service.files()
            .create(
                body=metadata,
                media_body=media,
                fields="id, name, webViewLink",
                supportsAllDrives=True,  # works for both My Drive and Shared drives
            )
            .execute()
        )
    except HttpError as e:
        status = getattr(getattr(e, "resp", None), "status", "?")

        # Pull Google's structured reason/message out of the response body.
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

        # Service accounts have no storage quota, so they cannot own files
        # in a personal (non-Workspace) Drive — even a shared folder.
        if reason == "storageQuotaExceeded" or "storage quota" in detail.lower():
            raise DriveError(
                "The service account has no storage quota of its own, so it "
                "cannot save files into a personal Google Drive folder. "
                "Use a Shared Drive (Google Workspace) with the service "
                "account added as a member, or switch to OAuth user "
                f"authentication. (Google: {detail or reason})"
            ) from e

        if reason == "accessNotConfigured":
            raise DriveError(
                "The Google Drive API is not enabled for this project. "
                "Enable it under APIs & Services → Library, then retry. "
                f"(Google: {detail or reason})"
            ) from e

        if str(status) == "404":
            raise DriveError(
                f"Folder '{folder_id}' not found or not shared with the "
                "service account. Share the folder with the service "
                f"account's client_email as Editor. (Google: {detail or reason})"
            ) from e

        if str(status) in ("401", "403"):
            raise DriveError(
                "Permission denied"
                + (f" ({reason})" if reason else "")
                + ". Confirm the folder is shared with the service account "
                "as Editor and the Drive API is enabled. "
                f"(Google: {detail})"
            ) from e

        raise DriveError(f"Drive upload failed (HTTP {status}): {detail or e}") from e
    except Exception as e:
        raise DriveError(f"Drive upload failed: {e}") from e

    return created
