"""Helpers for uploading generated podcast videos to Google Drive.

This module uses a Google service account stored in Streamlit secrets.
Do not commit the real service-account JSON file to GitHub.
"""

from __future__ import annotations

import json
import mimetypes
from pathlib import Path
from typing import Any, Callable, Mapping

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

DEFAULT_GOOGLE_DRIVE_FOLDER_ID = "1M53kFacEkHVE8UTU3j4jqOFLJxWVD7Cp"
DRIVE_SCOPES = ("https://www.googleapis.com/auth/drive",)


class GoogleDriveUploadError(RuntimeError):
    """Raised when Google Drive upload configuration or API upload fails."""


def _to_plain_dict(value: Any) -> dict[str, Any]:
    """Convert Streamlit's secrets mapping into a normal dictionary."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise GoogleDriveUploadError(
                "GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON. Paste the full service-account JSON value."
            ) from exc

    try:
        return dict(value)
    except Exception as exc:  # noqa: BLE001 - keep error readable in Streamlit UI
        raise GoogleDriveUploadError(
            "Service-account credentials must be a TOML table or JSON string in Streamlit secrets."
        ) from exc


def get_service_account_info_from_secrets(secrets: Mapping[str, Any]) -> dict[str, Any]:
    """Load service-account credentials from Streamlit secrets.

    Supported formats:
      1. [gdrive_service_account] TOML table with fields from the JSON key file.
      2. GOOGLE_SERVICE_ACCOUNT_JSON = '''{...}''' JSON string.
    """
    raw_credentials: Any | None = None

    try:
        if "gdrive_service_account" in secrets:
            raw_credentials = secrets["gdrive_service_account"]
        elif "google_service_account" in secrets:
            raw_credentials = secrets["google_service_account"]
        elif "GOOGLE_SERVICE_ACCOUNT_JSON" in secrets:
            raw_credentials = secrets["GOOGLE_SERVICE_ACCOUNT_JSON"]
    except Exception as exc:  # noqa: BLE001 - Streamlit raises a readable secrets error
        raise GoogleDriveUploadError(
            "Google Drive upload is enabled, but Streamlit secrets are not configured."
        ) from exc

    if raw_credentials is None:
        raise GoogleDriveUploadError(
            "Missing Google Drive service-account credentials. Add [gdrive_service_account] to Streamlit secrets."
        )

    info = _to_plain_dict(raw_credentials)

    if "private_key" in info and isinstance(info["private_key"], str):
        # Streamlit/TOML often stores the private key with escaped newlines.
        info["private_key"] = info["private_key"].replace("\\n", "\n")

    required = {"type", "project_id", "private_key", "client_email", "token_uri"}
    missing = sorted(required - set(info))
    if missing:
        raise GoogleDriveUploadError(
            f"Service-account credentials are missing required fields: {', '.join(missing)}"
        )

    return info


def upload_file_to_drive(
    file_path: str | Path,
    folder_id: str,
    service_account_info: Mapping[str, Any],
    uploaded_name: str | None = None,
    progress_cb: Callable[[int], None] | None = None,
) -> dict[str, Any]:
    """Upload a file to a Google Drive folder and return Drive file metadata."""
    path = Path(file_path)
    if not path.exists():
        raise GoogleDriveUploadError(f"File not found for Drive upload: {path}")
    if not folder_id:
        raise GoogleDriveUploadError("Google Drive folder ID is empty.")

    try:
        credentials = service_account.Credentials.from_service_account_info(
            dict(service_account_info),
            scopes=DRIVE_SCOPES,
        )
        service = build("drive", "v3", credentials=credentials, cache_discovery=False)

        mime_type, _ = mimetypes.guess_type(str(path))
        file_metadata = {
            "name": uploaded_name or path.name,
            "parents": [folder_id],
        }
        media = MediaFileUpload(
            str(path),
            mimetype=mime_type or "application/octet-stream",
            chunksize=10 * 1024 * 1024,
            resumable=True,
        )

        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id,name,webViewLink,webContentLink",
            supportsAllDrives=True,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status and progress_cb:
                progress_cb(int(status.progress() * 100))

        if progress_cb:
            progress_cb(100)
        return dict(response)

    except HttpError as exc:
        details = getattr(exc, "reason", None) or str(exc)
        raise GoogleDriveUploadError(f"Google Drive API upload failed: {details}") from exc
    except GoogleDriveUploadError:
        raise
    except Exception as exc:  # noqa: BLE001 - keep Streamlit error user-friendly
        raise GoogleDriveUploadError(f"Google Drive upload failed: {exc}") from exc
