
import os
import re
import time
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st
import whisper
import yt_dlp


# --- Page Configuration ---
st.set_page_config(
    page_title="AI Audio & Video Caption Generator",
    page_icon="🎙️",
    layout="centered"
)


# --- Professional UI Styling (Preserved) ---
custom_css = """
<style>
#MainMenu, footer, header, .stDeployButton,
div[data-testid="stStatusWidget"] {
    visibility: hidden !important;
    display: none !important;
}

.main .block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 3rem;
    margin: 0 auto;
}

h1, h2, h3, p {
    text-align: center;
}

.hero-box {
    background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
    padding: 30px;
    border-radius: 16px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
}

.hero-box h1 {
    color: white !important;
    font-size: 28px;
    margin-bottom: 10px;
}

.hero-box p {
    color: #e2e8f0 !important;
    font-size: 15px;
    margin: 0;
}

.tip-box {
    background-color: #eff6ff;
    border-left: 4px solid #4f46e5;
    padding: 14px 18px;
    border-radius: 8px;
    color: #1e3a8a;
    font-size: 14px;
    margin-bottom: 25px;
    text-align: left;
}

[data-testid="stFileUploader"],
[data-testid="stTextInput"] {
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
}

.stButton > button {
    display: block;
    width: 100%;
    max-width: 320px;
    margin: 15px auto !important;
    background-color: #4f46e5 !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    border-radius: 10px !important;
    padding: 12px 20px !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
    cursor: pointer !important;
}

.stButton > button:hover {
    background-color: #4338ca !important;
    box-shadow: 0 6px 18px rgba(67, 56, 202, 0.4) !important;
}

.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)


# --- Hero Header ---
st.markdown("""
<div class="hero-box">
    <h1>🎙️ AI Audio & Video Caption Generator</h1>
    <p>Generate accurate timestamps & subtitles automatically using OpenAI Whisper.</p>
</div>
""", unsafe_allow_html=True)


# --- Recommendation Notice ---
st.markdown("""
<div class="tip-box">
    💡 <b>Pro Tip:</b> Aap direct <b>Audio/Video File Upload</b>
    bhi kar sakte hain ya phir <b>YouTube Link</b> paste karke
    captions generate kar sakte hain!
</div>
""", unsafe_allow_html=True)


# --- Load Whisper Model ---
@st.cache_resource
def load_model():
    return whisper.load_model("base")


with st.spinner("Initializing AI Engine..."):
    model = load_model()


# --- Validate YouTube URL ---
def validate_youtube_url(url):
    try:
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()

        allowed_hosts = {
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "music.youtube.com",
            "youtu.be",
            "www.youtube-nocookie.com",
            "youtube-nocookie.com",
        }

        if parsed.scheme not in ("http", "https"):
            return False

        if host not in allowed_hosts:
            return False

        if host.endswith("youtu.be"):
            return bool(parsed.path.strip("/"))

        return (
            parsed.path == "/watch" and bool(parsed.query)
        ) or parsed.path.startswith(("/shorts/", "/embed/", "/live/"))

    except (ValueError, TypeError):
        return False


# --- Download Audio from YouTube ---
def download_youtube_audio(url, output_dir):
    """
    Download accessible YouTube audio using yt-dlp.
    Returns the downloaded audio file path.
    """
    if not validate_youtube_url(url):
        raise ValueError(
            "Please enter a valid YouTube video URL."
        )

    options = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "youtube_audio.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 2,
        "fragment_retries": 2,
        "socket_timeout": 20,
        "max_filesize": 200 * 1024 * 1024,
        "cachedir": False,
    }

    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([url])

    except Exception as exc:
        error_text = str(exc).lower()

        if "403" in error_text or "forbidden" in error_text:
            raise RuntimeError(
                "YouTube refused the media request (HTTP 403). "
                "Update yt-dlp and redeploy the app. If the error "
                "continues, the video may require authentication or "
                "the hosting IP may be restricted. Try uploading "
                "the media file instead."
            ) from exc

        if "sign in" in error_text or "login" in error_text:
            raise RuntimeError(
                "This video may require sign-in or additional access "
                "permissions. Please try another accessible video "
                "or upload the media file."
            ) from exc

        raise RuntimeError(
            f"Could not download YouTube audio: {str(exc)[:400]}"
        ) from exc

    # Find the actual downloaded format; do not assume it is MP4.
    candidates = [
        path for path in Path(output_dir).glob("youtube_audio.*")
        if path.is_file()
    ]

    if not candidates:
        raise RuntimeError(
            "Download finished, but no audio file was found."
        )

    # Select the largest candidate if more than one exists.
    audio_file = max(candidates, key=lambda path: path.stat().st_size)

    if audio_file.stat().st_size == 0:
        raise RuntimeError("The downloaded audio file is empty.")

    return str(audio_file)


# --- Caption Formatting ---
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    whole_seconds = int(seconds % 60)
    milliseconds = int(round((seconds - int(seconds)) * 1000))

    if milliseconds == 1000:
        whole_seconds += 1
        milliseconds = 0

    if whole_seconds == 60:
        minutes += 1
        whole_seconds = 0

    if minutes == 60:
        hours += 1
        minutes = 0

    return (
        f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},"
        f"{milliseconds:03d}"
    )


def format_captions(result):
    readable_lines = []
    srt_blocks = []

    for index, segment in enumerate(result.get("segments", []), start=1):
        start = float(segment["start"])
        end = float(segment["end"])
        text = segment["text"].strip()

        start_minutes = int(start // 60)
        start_seconds = int(start % 60)
        end_minutes = int(end // 60)
        end_seconds = int(end % 60)

        readable_lines.append(
            f"[{start_minutes:02d}:{start_seconds:02d} - "
            f"{end_minutes:02d}:{end_seconds:02d}] {text}"
        )

        srt_blocks.append(
            f"{index}\n"
            f"{format_timestamp(start)} --> {format_timestamp(end)}\n"
            f"{text}\n"
        )

    formatted_text = "\n".join(readable_lines).strip()
    srt_text = "\n".join(srt_blocks).strip()

    # Fallback if Whisper returns no segments.
    if not formatted_text:
        formatted_text = result.get("text", "").strip()

    if not srt_text:
        srt_text = formatted_text

    return formatted_text, srt_text


# --- Tabs ---
tab1, tab2 = st.tabs([
    "📁 Method 1: Upload File",
    "🔗 Method 2: YouTube Link"
])

uploaded_file = None
media_url = ""

with tab1:
    uploaded_file = st.file_uploader(
        "Select an audio or video file (.mp3, .wav, .mp4, .m4a)",
        type=["mp3", "wav", "mp4", "m4a"]
    )

with tab2:
    media_url = st.text_input(
        "Enter YouTube Video Link:",
        placeholder="https://www.youtube.com/watch?v=..."
    )

st.markdown("---")


# --- Process Button ---
generate_btn = st.button(
    "🚀 Generate Captions Now",
    type="primary"
)


if generate_btn:
    if uploaded_file is None and not media_url.strip():
        st.warning(
            "⚠️ Please upload a file OR enter a YouTube link first!"
        )

    elif uploaded_file is not None and media_url.strip():
        st.warning(
            "Please select only one method: upload a file "
            "OR provide a YouTube link."
        )

    elif media_url.strip() and not validate_youtube_url(media_url):
        st.error(
            "❌ Invalid YouTube URL. Please paste a valid video link."
        )

    else:
        work_dir = tempfile.mkdtemp(prefix="caption_generator_")
        audio_path = None
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # --- Option 1: File Upload ---
            if uploaded_file is not None:
                status_text.info("📥 Processing uploaded file...")
                progress_bar.progress(20)

                original_name = Path(uploaded_file.name).name
                suffix = Path(original_name).suffix.lower()

                if suffix not in {".mp3", ".wav", ".mp4", ".m4a"}:
                    raise ValueError("Unsupported file type.")

                audio_path = os.path.join(
                    work_dir, f"uploaded_media{suffix}"
                )

                with open(audio_path, "wb") as output_file:
                    output_file.write(uploaded_file.getbuffer())

                progress_bar.progress(50)

            # --- Option 2: YouTube ---
            else:
                status_text.info(
                    "⏳ Downloading audio from YouTube... Please wait."
                )
                progress_bar.progress(15)

                audio_path = download_youtube_audio(
                    media_url.strip(),
                    work_dir
                )

                progress_bar.progress(50)

            if not audio_path or not os.path.isfile(audio_path):
                raise RuntimeError(
                    "The audio file is unavailable for transcription."
                )

            if os.path.getsize(audio_path) == 0:
                raise RuntimeError("The media file is empty.")

            # --- Whisper Transcription ---
            status_text.info(
                "🤖 AI is listening & generating captions..."
            )
            progress_bar.progress(65)

            result = model.transcribe(audio_path)

            progress_bar.progress(90)

            formatted_text, srt_text = format_captions(result)

            if not formatted_text.strip():
                raise RuntimeError(
                    "No speech transcript was generated for this media."
                )

            progress_bar.progress(100)
            status_text.success(
                "🎉 Captions Generated Successfully!"
            )

            st.subheader("Your Subtitles:")

            st.text_area(
                "Captions Output",
                value=formatted_text,
                height=300
            )

            st.subheader("📥 Download Subtitles File")

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="📄 Download .SRT File",
                    data=srt_text,
                    file_name="captions.srt",
                    mime="application/x-subrip"
                )

            with col2:
                st.download_button(
                    label="📝 Download .TXT File",
                    data=formatted_text,
                    file_name="transcript.txt",
                    mime="text/plain"
                )

        except Exception as exc:
            status_text.empty()
            progress_bar.empty()
            st.error(f"❌ {str(exc)}")

        finally:
            # Clean uploaded and downloaded media from temporary storage.
            shutil.rmtree(work_dir, ignore_errors=True)


# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #64748b; "
    "font-size: 13px;'>Powered by OpenAI Whisper • "
    "Built for Content Creators</p>",
    unsafe_allow_html=True
)
