# 🎙️ Podcast Video Creator

Upload a thumbnail template + audio file → get a branded MP4 video with text overlay.

## Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Deploy!

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

> **Note:** ffmpeg must be installed on your system.

## Optional: Montserrat Fonts

For best results, download [Montserrat](https://fonts.google.com/specimen/Montserrat) and place the `.ttf` files in a `fonts/` folder:

```
fonts/
  Montserrat-ExtraBold.ttf
  Montserrat-Medium.ttf
```

If not found, Liberation Sans (installed via `packages.txt`) is used as fallback.

## Save to Google Drive setup

The app can upload the generated `.mp4` and thumbnail straight into a
Google Drive folder. A deployed app can't write to a folder from just a
share link — Google requires authenticated credentials — so this uses a
**service account** (no login pop-up needed).

1. In [Google Cloud Console](https://console.cloud.google.com/): create a
   project, enable the **Google Drive API**, then create a **service
   account** and download its **JSON key**.
2. Open the target Drive folder, click **Share**, and give the service
   account's `client_email` (from the JSON) **Editor** access.
3. Add the JSON to secrets — locally copy
   `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml` and fill
   it in, or on Streamlit Cloud paste it under **Settings → Secrets**
   using the same `[gcp_service_account]` block.

The destination folder ID (`1M53kFacEkHVE8UTU3j4jqOFLJxWVD7Cp`, from the
link you provided) is set in `drive_utils.py` as `DEFAULT_FOLDER_ID`.
Change it there to target a different folder.

> **Note on "OneDrive":** the request mentioned OneDrive, but the folder
> link supplied was Google Drive, so the button uploads to Google Drive.
> For true Microsoft OneDrive you'd swap `drive_utils.py` for the
> Microsoft Graph API (app registration in Entra ID + OAuth). Happy to
> add that instead if OneDrive is what you actually want.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI |
| `podcast_creator.py` | Thumbnail + video rendering logic |
| `requirements.txt` | Python dependencies |
| `packages.txt` | System packages (ffmpeg, fonts) for Streamlit Cloud |
| `.streamlit/config.toml` | Theme + upload size config |
| `fonts/` | *(optional)* Montserrat font files |
