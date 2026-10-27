
import os
import re
import tempfile
from pathlib import Path

import streamlit as st
import whisper
import requests

# Optional YouTube support
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


# -------------------- PAGE CONFIG --------------------

st.set_page_config(
    page_title="AI Audio & Video Caption Generator",
    page_icon="🎙️",
    layout="centered"
)

st.markdown("""
<style>
    .block-container {
        max-width: 850px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .hero {
        padding: 25px 18px;
        border-radius: 18px;
        text-align: center;
        color: white;
        background: linear-gradient(120deg, #6548e8, #2878d7);
        margin-bottom: 20px;
    }
    .hero h1 {
        font-size: 30px;
        margin-bottom: 8px;
    }
    .hero p {
        font-size: 15px;
        margin: 0;
    }
    .tip {
        padding: 12px;
        border-radius: 10px;
        background: rgba(120, 120, 150, 0.10);
        margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🎙️ AI Audio & Video Caption Generator</h1>
    <p>Generate captions from audio and video, then translate them.</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="tip">💡 Upload an audio/video file, select the caption language, '
    'and optionally translate the captions into another language.</div>',
    unsafe_allow_html=True
)


# -------------------- SETTINGS --------------------

LANGUAGES = {
    "English": "en",
    "Urdu": "ur",
    "Arabic": "ar",
    "Chinese (Simplified)": "zh",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Persian": "fa",
    "Portuguese": "pt",
    "Russian": "ru",
    "Spanish": "es",
    "Turkish": "tr",
    "Bengali": "bn",
    "Indonesian": "id",
    "Dutch": "nl",
    "Polish": "pl",
    "Thai": "th",
    "Vietnamese": "vi"
}

LIBRETRANSLATE_URL = os.getenv(
    "LIBRETRANSLATE_URL",
    "https://libretranslate.com"
).rstrip("/")

LIBRETRANSLATE_API_KEY = os.getenv("LIBRETRANSLATE_API_KEY", "S5eLorXfuLQ2TucA9kqsSSdGjr0-ckEE1QEXIiDpHUI")


# -------------------- WHISPER MODEL --------------------

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")


# -------------------- CAPTION HELPERS --------------------

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp: HH:MM:SS,mmm."""
    milliseconds = max(0, round(float(seconds) * 1000))

    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000

    minutes = milliseconds // 60_000
    milliseconds %= 60_000

    secs = milliseconds // 1000
    milliseconds %= 1000

    return (
        f"{hours:02}:{minutes:02}:{secs:02},"
        f"{milliseconds:03}"
    )


def create_srt(segments):
    output = []

    for index, segment in enumerate(segments, start=1):
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        text = str(segment["text"]).strip()

        output.append(
            f"{index}\n{start} --> {end}\n{text}\n"
        )

    return "\n".join(output)


def create_txt(segments):
    lines = []

    for segment in segments:
        start = float(segment["start"])
        end = float(segment["end"])
        text = str(segment["text"]).strip()

        start_label = (
            f"{int(start // 60):02}:{int(start % 60):02}"
        )
        end_label = (
            f"{int(end // 60):02}:{int(end % 60):02}"
        )

        lines.append(f"[{start_label} - {end_label}] {text}")

    return "\n".join(lines)


def transcribe_audio(file_path, source_language):
    model = load_whisper_model()

    options = {"fp16": False}

    if source_language != "Auto Detect":
        options["language"] = LANGUAGES[source_language]

    result = model.transcribe(file_path, **options)

    segments = []

    for item in result.get("segments", []):
        segments.append({
            "start": float(item.get("start", 0)),
            "end": float(item.get("end", 0)),
            "text": str(item.get("text", "")).strip()
        })

    detected_code = result.get("language", "")
    detected_name = next(
        (
            name for name, code in LANGUAGES.items()
            if code == detected_code
        ),
        detected_code or "Unknown"
    )

    return segments, detected_name


# -------------------- LIBRETRANSLATE --------------------

def translate_text(text, source_code, target_code):
    """Translate text using a LibreTranslate-compatible API."""

    endpoint = f"{LIBRETRANSLATE_URL}/translate"

    payload = {
        "q": text,
        "source": source_code,
        "target": target_code,
        "format": "text"
    }

    if LIBRETRANSLATE_API_KEY:
        payload["api_key"] = LIBRETRANSLATE_API_KEY

    response = requests.post(
        endpoint,
        data=payload,
        timeout=60
    )

    if not response.ok:
        raise RuntimeError(
            f"Translation service returned HTTP {response.status_code}. "
            "The service may be unavailable, rate-limited, or require an API key."
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "Translation service returned an invalid response."
        ) from exc

    translated = data.get("translatedText")

    if not isinstance(translated, str):
        raise RuntimeError(
            "Translation service response did not contain translatedText."
        )

    return translated


def translate_segments(segments, source_code, target_code):
    """Translate each subtitle segment while preserving timestamps."""

    translated_segments = []

    total = len(segments)
    progress = st.progress(0)
    status = st.empty()

    for index, segment in enumerate(segments):
        original_text = segment["text"].strip()

        if not original_text:
            translated_text = ""
        else:
            translated_text = translate_text(
                original_text,
                source_code,
                target_code
            )

        translated_segments.append({
            "start": segment["start"],
            "end": segment["end"],
            "text": translated_text.strip()
        })

        progress.progress((index + 1) / max(total, 1))
        status.caption(
            f"Translating caption {index + 1} of {total}..."
        )

    status.empty()
    progress.empty()

    return translated_segments


# -------------------- PROCESSING UI --------------------

def show_caption_results(segments, detected_language, source_code):
    if not segments:
        st.error("No speech was detected in this file.")
        return

    st.success(f"Transcription complete. Detected language: {detected_language}")

    original_srt = create_srt(segments)
    original_txt = create_txt(segments)

    st.subheader("Original Captions")

    with st.expander("Preview original captions", expanded=True):
        st.text(original_txt[:12000])

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "⬇️ Download Original SRT",
            data=original_srt,
            file_name="captions_original.srt",
            mime="application/x-subrip",
            key="download_original_srt"
        )

    with col2:
        st.download_button(
            "⬇️ Download Original TXT",
            data=original_txt,
            file_name="captions_original.txt",
            mime="text/plain",
            key="download_original_txt"
        )

    st.divider()
    st.subheader("Translate Captions")

    target_language = st.selectbox(
        "Select target language",
        options=list(LANGUAGES.keys()),
        index=0,
        key="target_language"
    )

    target_code = LANGUAGES[target_language]

    if st.button("🌐 Translate Captions", type="primary"):
        if source_code == target_code:
            st.warning(
                "The selected target language matches the transcription "
                "language. Choose a different target language."
            )
            return

        try:
            with st.spinner("Translating captions..."):
                translated = translate_segments(
                    segments,
                    source_code,
                    target_code
                )

            st.session_state["translated_segments"] = translated
            st.session_state["translated_language"] = target_language

        except requests.exceptions.Timeout:
            st.error(
                "Translation timed out. Please try again or use another "
                "LibreTranslate server."
            )
        except requests.exceptions.RequestException as exc:
            st.error(
                f"Could not connect to the translation service: {exc}"
            )
        except Exception as exc:
            st.error(f"Translation failed: {exc}")

    translated = st.session_state.get("translated_segments")
    saved_language = st.session_state.get("translated_language")

    if translated and saved_language:
        st.subheader(f"Translated Captions — {saved_language}")

        translated_srt = create_srt(translated)
        translated_txt = create_txt(translated)

        with st.expander("Preview translated captions", expanded=True):
            st.text(translated_txt[:12000])

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "⬇️ Download Translated SRT",
                data=translated_srt,
                file_name=f"captions_{LANGUAGES[saved_language]}.srt",
                mime="application/x-subrip",
                key="download_translated_srt"
            )

        with col2:
            st.download_button(
                "⬇️ Download Translated TXT",
                data=translated_txt,
                file_name=f"captions_{LANGUAGES[saved_language]}.txt",
                mime="text/plain",
                key="download_translated_txt"
            )


# -------------------- TABS --------------------

upload_tab, youtube_tab = st.tabs([
    "📁 Upload Audio / Video",
    "▶️ YouTube Link"
])


# -------------------- UPLOAD TAB --------------------

with upload_tab:
    uploaded_file = st.file_uploader(
        "Choose an audio or video file",
        type=[
            "mp3", "wav", "mp4", "m4a", "mpeg",
            "mpga", "webm", "ogg", "oga", "flac"
        ]
    )

    source_language = st.selectbox(
        "Transcription language",
        options=["Auto Detect"] + list(LANGUAGES.keys()),
        index=0,
        key="source_language_upload"
    )

    if uploaded_file is not None:
        if st.button("🎙️ Generate Captions", type="primary"):
            temp_path = None

            try:
                suffix = Path(uploaded_file.name).suffix or ".mp4"

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                ) as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    temp_path = temp_file.name

                with st.spinner(
                    "Transcribing audio/video. This may take some time..."
                ):
                    segments, detected_language = transcribe_audio(
                        temp_path,
                        source_language
                    )

                st.session_state["original_segments"] = segments
                st.session_state["detected_language"] = detected_language

                st.session_state.pop("translated_segments", None)
                st.session_state.pop("translated_language", None)

            except Exception as exc:
                st.error(f"Transcription failed: {exc}")

            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

    if st.session_state.get("original_segments"):
        detected_language = st.session_state.get(
            "detected_language", "Unknown"
        )

        detected_code = next(
            (
                code for name, code in LANGUAGES.items()
                if name == detected_language
            ),
            None
        )

        if detected_code is None:
            detected_code = "en"

        show_caption_results(
            st.session_state["original_segments"],
            detected_language,
            detected_code
        )


# -------------------- YOUTUBE TAB --------------------

with youtube_tab:
    st.info(
        "YouTube downloading may fail because of platform restrictions. "
        "If it fails, download the media through a method permitted by "
        "the content owner and upload the file in the first tab."
    )

    youtube_url = st.text_input(
        "YouTube video URL",
        placeholder="https://www.youtube.com/watch?v=..."
    )

    youtube_source_language = st.selectbox(
        "Transcription language for YouTube",
        options=["Auto Detect"] + list(LANGUAGES.keys()),
        index=0,
        key="source_language_youtube"
    )

    if st.button("▶️ Process YouTube Link"):
        if not youtube_url.strip():
            st.warning("Please enter a YouTube URL.")
        elif not YT_DLP_AVAILABLE:
            st.error(
                "YouTube support is not installed. Add yt-dlp to "
                "requirements.txt and redeploy the app."
            )
        elif not re.match(
            r"^https?://(www\.)?(youtube\.com|youtu\.be)/",
            youtube_url.strip()
        ):
            st.error("Please enter a valid YouTube URL.")
        else:
            temp_dir = tempfile.mkdtemp(prefix="caption_")
            downloaded_path = None

            try:
                output_template = os.path.join(
                    temp_dir, "media.%(ext)s"
                )

                options = {
                    "format": "bestaudio/best",
                    "outtmpl": output_template,
                    "noplaylist": True,
                    "quiet": True,
                    "no_warnings": True
                }

                with st.spinner("Attempting to retrieve media..."):
                    with yt_dlp.YoutubeDL(options) as ydl:
                        ydl.download([youtube_url.strip()])

                candidates = [
                    os.path.join(temp_dir, filename)
                    for filename in os.listdir(temp_dir)
                    if os.path.isfile(os.path.join(temp_dir, filename))
                ]

                if not candidates:
                    raise RuntimeError(
                        "The media could not be downloaded."
                    )

                downloaded_path = candidates[0]

                with st.spinner("Transcribing downloaded media..."):
                    segments, detected_language = transcribe_audio(
                        downloaded_path,
                        youtube_source_language
                    )

                st.session_state["original_segments"] = segments
                st.session_state["detected_language"] = detected_language
                st.session_state.pop("translated_segments", None)
                st.session_state.pop("translated_language", None)

                st.rerun()

            except Exception as exc:
                st.error(
                    "Could not process this YouTube video. YouTube may "
                    "be blocking the request (HTTP 403). Try uploading "
                    "the audio/video file instead. Details: "
                    f"{exc}"
                )

            finally:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)


# -------------------- FOOTER --------------------

st.divider()
st.caption(
    "   "
    "   "
)
