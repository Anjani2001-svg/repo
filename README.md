# Podcast Video Creator

Streamlit app that creates a branded MP4 podcast video from an audio upload, course name, and unit name.

This version includes an optional **Google Drive upload** step after the final video is rendered. The uploaded target defaults to this folder ID:

```text
1M53kFacEkHVE8UTU3j4jqOFLJxWVD7Cp
```

> Note: the link you provided is a Google Drive folder, not OneDrive. This app uses Google Drive API + Google service account credentials. True Microsoft OneDrive upload would need Microsoft Graph OAuth instead.

## Files changed for Google Drive upload

| File | Purpose |
|---|---|
| `app.py` | Adds a checkbox to upload the final MP4 to Google Drive after rendering. |
| `google_drive_uploader.py` | Handles service-account auth and resumable MP4 upload. |
| `requirements.txt` | Adds Google API client dependencies. |
| `.streamlit/secrets.example.toml` | Example credentials format for local/Streamlit deployment. |
| `.gitignore` | Prevents real secrets and generated videos from being committed. |

## Google Drive setup

1. In Google Cloud Console, enable **Google Drive API** for your project.
2. Create or select a **service account**.
3. Create a JSON key for the service account and download it.
4. Copy the service account email, for example:

   ```text
   your-service-account@your-project-id.iam.gserviceaccount.com
   ```

5. Open the Google Drive folder you want to upload into.
6. Share the folder with the service account email and give it **Editor** permission.

Your folder link was:

```text
https://drive.google.com/drive/folders/1M53kFacEkHVE8UTU3j4jqOFLJxWVD7Cp?usp=sharing
```

So the folder ID is:

```text
1M53kFacEkHVE8UTU3j4jqOFLJxWVD7Cp
```

## Local Streamlit secrets

Copy the example file:

```bash
mkdir -p .streamlit
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
```

Then paste your real service-account JSON values into `.streamlit/secrets.toml`:

```toml
GDRIVE_FOLDER_ID = "1M53kFacEkHVE8UTU3j4jqOFLJxWVD7Cp"

[gdrive_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nPASTE_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

Do not commit `.streamlit/secrets.toml` to GitHub.

## Streamlit Cloud deployment

1. Push the project to GitHub.
2. Open Streamlit Cloud and deploy with `app.py` as the main file.
3. Open your app settings and paste the same secrets content from above into **Secrets**.
4. Make sure the Google Drive folder is shared with the service account email.
5. Reboot/redeploy the Streamlit app.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

`ffmpeg` and `ffprobe` must be installed. On Streamlit Cloud, `packages.txt` should install system packages such as ffmpeg.

## Upload behavior

When you click **Create Video**, the app:

1. Creates the thumbnail.
2. Renders the MP4.
3. Saves the MP4 locally in `videos/`.
4. If the checkbox **Upload final video to Google Drive** is enabled, uploads the MP4 to the configured Google Drive folder.
5. Shows a Google Drive link if the upload succeeds.

If Google Drive upload fails, the app still keeps the generated local video and shows the normal download button.
