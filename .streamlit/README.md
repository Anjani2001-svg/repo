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

The app uploads the generated `.mp4` into your Google Drive folder. It
uploads **as you** using OAuth, because a service account has no storage
quota of its own and cannot save into a personal (non-Workspace) Drive.
You authorize once to produce a refresh token; after that the app uploads
without any login screen.

### 1. Create an OAuth client in Google Cloud

1. In [Google Cloud Console](https://console.cloud.google.com/) select (or
   create) a project and enable the **Google Drive API**
   (*APIs & Services → Library*).
2. Go to *APIs & Services → OAuth consent screen*: choose **External**,
   fill in the basics, and **set the publishing status to "In production"**.
   (If you leave it in "Testing", Google revokes the refresh token after 7
   days. Production needs no verification for personal use under 100 users
   — you just click past the "unverified app" warning when authorizing.)
3. Go to *APIs & Services → Credentials → Create credentials → OAuth client
   ID*, choose application type **Desktop app**, create it, and **download
   the JSON**. Rename it to `client_secret.json`.

### 2. Get a refresh token (run once, locally)

```bash
pip install google-auth-oauthlib
python generate_token.py        # client_secret.json must be in this folder
```

A browser opens — sign in as the account that owns the destination folder
and approve. The script prints a ready-to-paste `[google_oauth]` block.

### 3. Add the credentials to secrets

Paste that block into Streamlit Cloud (*Settings → Secrets*), or locally
copy `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml` and fill
in `client_id`, `client_secret`, and `refresh_token`.

The destination folder ID (`1M53kFacEkHVE8UTU3j4jqOFLJxWVD7Cp`, from the
link you provided) is set in `drive_utils.py` as `DEFAULT_FOLDER_ID`.
Change it there to target a different folder.

> **Note on "OneDrive":** the request mentioned OneDrive, but the folder
> link supplied was Google Drive, so the button uploads to Google Drive.
> For true Microsoft OneDrive you'd swap `drive_utils.py` for the
> Microsoft Graph API (app registration in Entra ID + OAuth).

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI |
| `podcast_creator.py` | Thumbnail + video rendering logic |
| `requirements.txt` | Python dependencies |
| `packages.txt` | System packages (ffmpeg, fonts) for Streamlit Cloud |
| `.streamlit/config.toml` | Theme + upload size config |
| `fonts/` | *(optional)* Montserrat font files |
