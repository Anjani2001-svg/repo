#!/usr/bin/env python3
"""
app.py – Podcast Video Creator (Streamlit)
Run locally:  streamlit run app.py

Only requires: Audio file + Course Name + Unit Name
Thumbnail template is generated automatically in code.
"""

import tempfile
import shutil
from pathlib import Path

import streamlit as st

from podcast_creator import create_thumbnail, create_video
import drive_utils

# ── Auto-create output folders next to the app ──
APP_DIR      = Path(__file__).parent
THUMB_FOLDER = APP_DIR / "thumbnails"
VIDEO_FOLDER = APP_DIR / "videos"
THUMB_FOLDER.mkdir(exist_ok=True)
VIDEO_FOLDER.mkdir(exist_ok=True)

# ── Page config ──
st.set_page_config(
    page_title="Podcast Video Creator",
    layout="centered",
)

# ── CDD design system (tokens + components) ──
# Implements the CDD UI/UX Standards Framework: consistent design tokens,
# WCAG 2.2 AA contrast, visible focus states, ≥16px body text, standard
# primary / secondary / danger buttons, and status badges that use an
# icon + text (never colour alone).
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    /* ---- Design tokens ---- */
    :root {
        --bg:            #07191c;
        --surface:       #0e2d31;
        --surface-2:     #122a2e;
        --border:        rgba(120,210,214,0.28);
        --border-strong: #2f8086;

        --text:          #eaf7f8;   /* body text on dark bg – high contrast */
        --text-muted:    #b6d6d9;
        --heading:       #ecffff;

        /* Primary (Create / Save) – solid teal, white text ≥4.5:1 */
        --primary:       #007a80;
        --primary-hover: #00666b;
        --on-primary:    #ffffff;

        /* Status colours – paired with icon + text, never colour alone */
        --success:       #36d39a;
        --success-bg:    rgba(54,211,154,0.12);
        --warning:       #f0b542;
        --warning-bg:    rgba(240,181,66,0.12);
        --danger:        #ff6b66;
        --danger-bg:     rgba(255,107,102,0.12);
        --info:          #4cc8d4;
        --info-bg:       rgba(76,200,212,0.12);

        --focus-ring:    #5fe0e8;

        --radius:        12px;
        --radius-sm:     8px;
        --space:         1rem;
    }

    html, body, .stApp, .stApp p, .stApp label, .stApp div {
        font-family: 'DM Sans', system-ui, -apple-system, sans-serif;
    }
    .stApp {
        background: var(--bg);
        color: var(--text);
        font-size: 16px;            /* §7 body text ≥16px */
        line-height: 1.55;
    }
    .block-container { max-width: 760px; }

    /* ---- Header (one bold H1 per page – §7) ---- */
    .app-header { text-align: center; padding: 1.6rem 0 0.6rem; }
    .app-header h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--heading);
        margin-bottom: 0.35rem;
    }
    .app-header p { color: var(--text-muted); font-size: 1rem; margin: 0; }

    /* ---- Section headings (§6 page structure / scanning) ---- */
    .sec-head {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--heading);
        margin: 1.6rem 0 0.6rem;
        padding-bottom: 0.45rem;
        border-bottom: 1px solid var(--border);
    }
    .field-legend { font-size: 0.9rem; color: var(--text-muted); margin: 0 0 0.4rem; }
    .req { color: var(--warning); font-weight: 700; }

    /* ---- Labels (§10 every field has a clear visible label) ---- */
    .stTextInput label, .stFileUploader label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--text) !important;
    }

    /* ---- Text inputs (accessible contrast + visible focus) ---- */
    .stTextInput > div > div > input {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 1rem !important;
        padding: 0.7rem 0.85rem !important;
    }
    .stTextInput > div > div > input::placeholder { color: #88b0b4 !important; }
    .stTextInput > div > div > input:focus,
    .stTextInput > div > div > input:focus-visible {
        border-color: var(--border-strong) !important;
        outline: 3px solid var(--focus-ring) !important;
        outline-offset: 1px !important;
        box-shadow: none !important;
    }

    /* ---- File uploader ---- */
    .stFileUploader > div {
        border: 2px dashed var(--border) !important;
        border-radius: var(--radius) !important;
        background: var(--surface) !important;
    }
    .stFileUploader > div:hover { border-color: var(--border-strong) !important; }
    .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] { color: var(--text-muted) !important; }

    /* ---- Primary buttons: Create / Save (§11) ---- */
    .stButton > button {
        width: 100%;
        min-height: 48px;           /* §14 large touch target */
        padding: 0.8rem 1rem;
        background: var(--primary) !important;
        color: var(--on-primary) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        border: 1px solid var(--primary) !important;
        border-radius: var(--radius-sm) !important;
    }
    .stButton > button:hover { background: var(--primary-hover) !important; border-color: var(--primary-hover) !important; }
    .stButton > button:focus-visible {
        outline: 3px solid var(--focus-ring) !important;
        outline-offset: 2px !important;
    }
    .stButton > button:disabled { opacity: 0.55 !important; cursor: not-allowed !important; }

    /* ---- Secondary buttons: Download (§11) ---- */
    .stDownloadButton > button {
        width: 100%;
        min-height: 48px;
        background: transparent !important;
        border: 1px solid var(--border-strong) !important;
        color: var(--text) !important;
        font-weight: 600 !important;
        border-radius: var(--radius-sm) !important;
    }
    .stDownloadButton > button:hover { background: rgba(47,128,134,0.18) !important; }
    .stDownloadButton > button:focus-visible {
        outline: 3px solid var(--focus-ring) !important;
        outline-offset: 2px !important;
    }

    /* ---- Result surface + status badges (§8 icon + text, not colour alone) ---- */
    .result-card {
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.25rem 1.4rem;
        margin-top: 1rem;
    }
    .result-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem; font-weight: 700; color: var(--heading);
        margin: 0 0 0.2rem;
    }
    .badge {
        display: inline-flex; align-items: center; gap: 0.4rem;
        font-size: 0.85rem; font-weight: 600;
        padding: 0.25rem 0.7rem; border-radius: 999px;
        border: 1px solid transparent;
    }
    .badge--success { color: var(--success); background: var(--success-bg); border-color: var(--success); }
    .badge--info    { color: var(--info);    background: var(--info-bg);    border-color: var(--info); }
    .badge--muted   { color: var(--text-muted); background: rgba(120,210,214,0.08); border-color: var(--border); }

    .saved-path {
        font-size: 0.9rem; color: var(--text-muted);
        margin: 0.15rem 0; word-break: break-all;
    }

    /* Links in results: visible + focusable */
    .stApp a { color: var(--info); text-decoration: underline; }
    .stApp a:focus-visible { outline: 3px solid var(--focus-ring); outline-offset: 2px; border-radius: 4px; }

    /* ---- Responsive (§14) ---- */
    @media (max-width: 640px) {
        .app-header h1 { font-size: 1.6rem; }
        .block-container { padding-left: 1rem; padding-right: 1rem; }
    }
    img { max-width: 100%; height: auto; }

    /* Keep a clean tool surface; main menu kept for accessibility/navigation */
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div class="app-header">
    <h1>Podcast Video Creator</h1>
    <p>Upload audio, enter the course and unit, then create your video.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<p class="field-legend"><span class="req">*</span> Required field</p>',
            unsafe_allow_html=True)

# ── Audio upload ──
st.markdown('<h2 class="sec-head">Audio file</h2>', unsafe_allow_html=True)

audio_file = st.file_uploader(
    "Audio file *",
    type=["mp3", "wav", "m4a", "aac", "ogg"],
    help="Accepted formats: MP3, WAV, M4A, AAC, OGG.",
)

# ── Episode details ──
st.markdown('<h2 class="sec-head">Course and unit details</h2>', unsafe_allow_html=True)

course = st.text_input(
    "Course name *",
    placeholder="e.g. Level 7 Extended Diploma in Computing Technologies (Networking) - RQF",
    help="The full course title as it should appear on the thumbnail.",
)
unit_name = st.text_input(
    "Unit number and unit name *",
    placeholder="e.g. Unit 01 - Managing Innovation and Change in Computing",
    help="Include the unit number and the unit title.",
)

# ── Create button ──
st.markdown("")
create_btn = st.button("Create video", use_container_width=True)

if create_btn:
    # ── Validation (§10: specific, actionable, shown per field) ──
    errors = []
    if not course or not course.strip():
        errors.append("Please enter the course name.")
    if not unit_name or not unit_name.strip():
        errors.append("Please enter the unit number and unit name.")
    if not audio_file:
        errors.append("Please upload an audio file (MP3, WAV, M4A, AAC or OGG).")

    if errors:
        for msg in errors:
            st.error(msg)
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            audio_path = tmpdir / f"audio{Path(audio_file.name).suffix}"
            audio_path.write_bytes(audio_file.getvalue())

            thumb_path = tmpdir / "thumbnail.jpg"
            video_path = tmpdir / "output.mp4"

            progress_bar = st.progress(0, text="Generating thumbnail…")

            try:
                # Step 1: Thumbnail (auto-generated template)
                create_thumbnail(course, unit_name, str(thumb_path))
                progress_bar.progress(5, text="Thumbnail created. Rendering video…")

                # Step 2: Video with progress
                def on_progress(pct: int, msg: str):
                    mapped = 5 + int(pct * 0.95)
                    progress_bar.progress(min(mapped, 100), text=msg)

                create_video(str(thumb_path), str(audio_path), str(video_path), progress_cb=on_progress)

                progress_bar.progress(100, text="Done!")

                # ── Auto-save to folders (these survive Streamlit reruns) ──
                safe_name = unit_name.replace(" ", "_").replace("/", "-")[:60]
                saved_thumb = THUMB_FOLDER / f"{safe_name}_thumbnail.jpg"
                saved_video = VIDEO_FOLDER / f"{safe_name}.mp4"
                shutil.copy2(thumb_path, saved_thumb)
                shutil.copy2(video_path, saved_video)

                # Persist results so download / Drive buttons work after the
                # rerun a button click triggers (the tmpdir is gone by then).
                st.session_state["result"] = {
                    "video_path": str(saved_video),
                    "thumb_path": str(saved_thumb),
                    "safe_name": safe_name,
                }
                # New render → clear any stale "uploaded" flag.
                st.session_state.pop("drive_uploaded", None)

            except Exception as e:
                progress_bar.empty()
                st.session_state.pop("result", None)
                st.error(f"Error: {e}")


# ── Results + Save-to-Drive (renders whenever a result exists) ──
result = st.session_state.get("result")
if result and Path(result["video_path"]).exists():
    video_path = Path(result["video_path"])
    thumb_path = Path(result["thumb_path"])
    safe_name = result["safe_name"]

    st.markdown("""
    <div class="result-card">
        <p class="result-title">Video created successfully</p>
        <span class="badge badge--success">✓ Ready</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<p class="saved-path">Video saved to: <code>videos/{video_path.name}</code></p>'
        f'<p class="saved-path">Thumbnail saved to: <code>thumbnails/{thumb_path.name}</code></p>',
        unsafe_allow_html=True,
    )

    st.image(str(thumb_path), caption="Generated thumbnail", use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        with open(video_path, "rb") as f:
            st.download_button(
                "Download video (MP4)",
                data=f,
                file_name="podcast_episode.mp4",
                mime="video/mp4",
                use_container_width=True,
            )
    with col_b:
        with open(thumb_path, "rb") as f:
            st.download_button(
                "Download thumbnail (JPG)",
                data=f,
                file_name="podcast_thumbnail.jpg",
                mime="image/jpeg",
                use_container_width=True,
            )

    # ── Save to Google Drive ──
    # NOTE: The folder link supplied was a Google Drive folder, so this
    # uploads there. See README for switching to actual OneDrive.
    st.markdown('<h2 class="sec-head">Cloud backup</h2>', unsafe_allow_html=True)

    sa_info = None
    try:
        if "google_oauth" in st.secrets:
            sa_info = dict(st.secrets["google_oauth"])
    except Exception:
        sa_info = None

    if sa_info is None:
        st.info(
            "**Save to Google Drive** is not configured yet. Run "
            "`generate_token.py` once to authorize, then add the "
            "`[google_oauth]` block to Streamlit secrets. See README -> "
            "*Save to Google Drive setup*."
        )
    else:
        if st.button("Save video to Google Drive", use_container_width=True):
            with st.spinner("Uploading video to Google Drive…"):
                try:
                    up_video = drive_utils.upload_file(
                        str(video_path),
                        f"{safe_name}.mp4",
                        sa_info,
                        mime_type="video/mp4",
                    )
                    st.session_state["drive_uploaded"] = {
                        "video_link": up_video.get("webViewLink", ""),
                    }
                except drive_utils.DriveError as e:
                    st.session_state.pop("drive_uploaded", None)
                    st.error(f"Drive upload failed: {e}")
                except Exception as e:
                    st.session_state.pop("drive_uploaded", None)
                    st.error(f"Unexpected error during upload: {e}")

        uploaded = st.session_state.get("drive_uploaded")
        if uploaded:
            st.markdown(
                '<span class="badge badge--success">✓ Video saved to Google Drive</span>',
                unsafe_allow_html=True,
            )
            if uploaded.get("video_link"):
                st.markdown(f"[Open video in Drive]({uploaded['video_link']})")
