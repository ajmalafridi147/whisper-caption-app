import os
import re
import tempfile
import shutil
from pathlib import Path

import streamlit as st
import whisper
import yt_dlp
from openai import OpenAI

st.set_page_config(
    page_title="AI Audio & Video Caption Generator",
    page_icon="🎙️",
    layout="centered",
)

# Preserve the original compact, centered design.
st.markdown(
    """
    
    <style>

/* Tabs ko center mein karne ke liye */
div[data-testid="stTabs"] {
    display: flex;
    flex-direction: column;
    align-items: center;
}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    justify-content: center;
    display: flex;
}

  
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    .block-container {max-width: 850px; padding-top: 1.5rem; padding-bottom: 2rem;}
    .hero {
        background: linear-gradient(120deg, #6548d7 0%, #3277e8 100%);
        color: white; padding: 25px 22px; border-radius: 16px;
        text-align: center; margin-bottom: 18px;
    }
    .hero h1 {font-size: 1.8rem; margin: 0 0 8px 0; color: white;}
    .hero p {font-size: 1rem; margin: 0; color: white;}
    .tip {
        background: #eef5ff; border-left: 5px solid #3779e8;
        color: #20324d; padding: 12px 15px; border-radius: 8px;
        margin: 12px 0 20px 0;
    }
    div.stButton > button, div.stDownloadButton > button {
        border-radius: 9px; font-weight: 600; width: 100%;
    }
    div[data-testid="stTabs"] button {justify-content: center;}
    .small-note {font-size: .88rem; color: #687386;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>🎙️ AI Audio &amp; Video Caption Generator</h1>
      <p>Generate accurate timestamps, original captions, and translated subtitles.</p>
    </div>
    <div class="tip">
      💡 <b>Pro tip:</b> For best results, use clear audio, and if the YouTube link cannot be downloaded, 
                please upload the media file instead.
    </div>
    """,
    unsafe_allow_html=True,
)

SUPPORTED_TYPES = ["mp3", "wav", "mp4", "m4a", "mpeg", "mpga", "webm", "ogg", "oga", "flac"]
LANGUAGES = {
    "English": "en",
    "Urdu": "ur",
    "Arabic": "ar",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese (Simplified)": "zh",
    "Portuguese": "pt",
    "Turkish": "tr",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Russian": "ru",
    "Bengali": "bn",
    "Punjabi": "pa",
    "Persian": "fa",
    "Indonesian": "id",
    "Dutch": "nl",
    "Polish": "pl",
    "Thai": "th",
    "Vietnamese": "vi",
    "Swahili": "sw",
}
LANG_CODE_TO_NAME = {v: k for k, v in LANGUAGES.items()}

@st.cache_resource(show_spinner="Loading Whisper model (first run may take a little while)...")
def load_whisper_model():
    return whisper.load_model("base")

def format_srt_time(seconds):
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    whole_seconds = int(seconds % 60)
    milliseconds = int(round((seconds - int(seconds)) * 1000))
    if milliseconds >= 1000:
        whole_seconds += 1
        milliseconds = 0
    if whole_seconds >= 60:
        minutes += 1
        whole_seconds = 0
    if minutes >= 60:
        hours += 1
        minutes = 0
    return f"{hours:02}:{minutes:02}:{whole_seconds:02},{milliseconds:03}"

def format_readable_time(seconds):
    total = max(0, int(seconds))
    return f"{total // 60:02}:{total % 60:02}"

def make_srt(segments):
    blocks = []
    for index, segment in enumerate(segments, start=1):
        text = str(segment.get("text", "")).strip()
        if not text:
            continue
        blocks.append(
            f"{index}\n"
            f"{format_srt_time(segment['start'])} --> {format_srt_time(segment['end'])}\n"
            f"{text}"
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")

def make_txt(segments):
    lines = []
    for segment in segments:
        text = str(segment.get("text", "")).strip()
        if text:
            lines.append(f"[{format_readable_time(segment['start'])} - {format_readable_time(segment['end'])}] {text}")
    return "\n".join(lines)

def safe_language_code(name):
    return LANGUAGES.get(name, "und")

def get_openai_api_key():
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("OPENAI_API_KEY", "")

def transcribe_media(media_path, source_language):
    model = load_whisper_model()
    kwargs = {"fp16": False, "verbose": False}
    if source_language != "Auto Detect":
        code = safe_language_code(source_language)
        if code != "und":
            kwargs["language"] = code
    result = model.transcribe(media_path, **kwargs)
    segments = []
    for item in result.get("segments", []):
        text = str(item.get("text", "")).strip()
        if text:
            segments.append({
                "start": float(item.get("start", 0.0)),
                "end": float(item.get("end", 0.0)),
                "text": text,
            })
    detected_code = result.get("language", "und")
    detected_name = LANG_CODE_TO_NAME.get(detected_code, detected_code.upper() if detected_code != "und" else "Unknown")
    return segments, detected_code, detected_name

def translate_segments(segments, target_language, api_key):
    """Translate batches of segment text while preserving original segment timing."""
    if not api_key:
        raise ValueError(
            "Translation API key is missing. Add OPENAI_API_KEY to Streamlit Cloud Secrets."
        )
    if not segments:
        return []
    client = OpenAI(api_key=api_key)
    translated = []
    batch_size = 35
    for start_index in range(0, len(segments), batch_size):
        batch = segments[start_index:start_index + batch_size]
        numbered_text = "\n".join(
            f"{i + 1}. {segment['text']}" for i, segment in enumerate(batch)
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Translate each numbered subtitle segment into {target_language}. "
                        "Return exactly the same number of numbered lines, in the same order. "
                        "Keep each translation concise for subtitles. Do not merge, split, "
                        "renumber, explain, or add lines. Preserve names and meaning. "
                        "Output only numbered translations."
                    ),
                },
                {"role": "user", "content": numbered_text},
            ],
        )
        response_text = response.choices[0].message.content or ""
        parsed = {}
        for line in response_text.splitlines():
            match = re.match(r"^\s*(\d+)[.)]\s*(.*?)\s*$", line)
            if match:
                parsed[int(match.group(1))] = match.group(2).strip()
        if len(parsed) != len(batch) or any(i not in parsed for i in range(1, len(batch) + 1)):
            raise ValueError(
                "Translation response could not be aligned safely with subtitle segments. "
                "Please try again."
            )
        for i, segment in enumerate(batch, start=1):
            translated.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": parsed[i],
            })
    return translated

def download_youtube_audio(url, destination):
    output_template = str(Path(destination) / "youtube_audio.%(ext)s")
    options = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 2,
        "socket_timeout": 20,
    }
    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=True)
        path = downloader.prepare_filename(info)
    if not os.path.exists(path):
        candidates = list(Path(destination).glob("youtube_audio.*"))
        if not candidates:
            raise FileNotFoundError("Downloaded audio file was not found.")
        path = str(candidates[0])
    return path

def display_results(segments, label, filename_prefix):
    if not segments:
        st.warning("No speech segments were found.")
        return
    st.subheader(label)
    st.text_area(
        f"{label} preview",
        make_txt(segments),
        height=240,
        key=f"preview_{filename_prefix}",
    )
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download SRT",
            data=make_srt(segments).encode("utf-8"),
            file_name=f"{filename_prefix}.srt",
            mime="application/x-subrip",
            key=f"srt_{filename_prefix}",
        )
    with col2:
        st.download_button(
            "⬇️ Download TXT",
            data=make_txt(segments).encode("utf-8"),
            file_name=f"{filename_prefix}.txt",
            mime="text/plain; charset=utf-8",
            key=f"txt_{filename_prefix}",
        )

if "original_segments" not in st.session_state:
    st.session_state.original_segments = None
if "translated_segments" not in st.session_state:
    st.session_state.translated_segments = None
if "detected_language_name" not in st.session_state:
    st.session_state.detected_language_name = None
if "detected_language_code" not in st.session_state:
    st.session_state.detected_language_code = None
if "translation_target" not in st.session_state:
    st.session_state.translation_target = None

upload_tab, youtube_tab = st.tabs(["📁 Method 1: Upload File", "🔗 Method 2: YouTube Link"])

with upload_tab:
    uploaded_file = st.file_uploader(
        "Upload an audio or video file",
        type=SUPPORTED_TYPES,
        help="Supported formats include MP3, WAV, MP4, M4A, WEBM, OGG, and FLAC.",
    )
    source_language = st.selectbox(
        "Spoken language",
        ["Auto Detect"] + list(LANGUAGES.keys()),
        index=0,
        help="Choose Auto Detect to let Whisper identify the spoken language.",
        key="upload_source_language",
    )
    if st.button("🚀 Generate Captions Now", type="primary", use_container_width=True, key="upload_transcribe"):
        if not uploaded_file:
            st.warning("Please upload an audio or video file first.")
        else:
            st.session_state.original_segments = None
            st.session_state.translated_segments = None
            with tempfile.TemporaryDirectory(prefix="caption_upload_") as work_dir:
                suffix = Path(uploaded_file.name).suffix or ".media"
                media_path = str(Path(work_dir) / f"uploaded_media{suffix}")
                with open(media_path, "wb") as file_handle:
                    file_handle.write(uploaded_file.getbuffer())
                try:
                    with st.spinner("Transcribing audio with Whisper..."):
                        segments, lang_code, lang_name = transcribe_media(media_path, source_language)
                    st.session_state.original_segments = segments
                    st.session_state.detected_language_code = lang_code
                    st.session_state.detected_language_name = lang_name
                    st.success(f"Transcription complete. Detected language: {lang_name}")
                except Exception as exc:
                    st.error(f"Transcription failed: {exc}")

with youtube_tab:
    st.info("If YouTube downloading returns HTTP 403, upload the media file using the first tab.")
    youtube_url = st.text_input("YouTube video URL", placeholder="https://www.youtube.com/watch?v=...")
    yt_source_language = st.selectbox(
        "Spoken language",
        ["Auto Detect"] + list(LANGUAGES.keys()),
        index=0,
        key="youtube_source_language",
    )
    if st.button("🚀 Generate Captions Now", type="primary", use_container_width=True, key="youtube_transcribe"):
        if not youtube_url.strip():
            st.warning("Please enter a YouTube URL.")
        elif not re.match(r"^https?://(www\.)?(youtube\.com|youtu\.be)/", youtube_url.strip(), re.I):
            st.warning("Please enter a valid YouTube or youtu.be URL.")
        else:
            st.session_state.original_segments = None
            st.session_state.translated_segments = None
            with tempfile.TemporaryDirectory(prefix="caption_youtube_") as work_dir:
                try:
                    with st.spinner("Attempting to download audio from YouTube..."):
                        media_path = download_youtube_audio(youtube_url.strip(), work_dir)
                    with st.spinner("Transcribing audio with Whisper..."):
                        segments, lang_code, lang_name = transcribe_media(media_path, yt_source_language)
                    st.session_state.original_segments = segments
                    st.session_state.detected_language_code = lang_code
                    st.session_state.detected_language_name = lang_name
                    st.success(f"Transcription complete. Detected language: {lang_name}")
                except Exception as exc:
                    message = str(exc)
                    if "403" in message or "Forbidden" in message:
                        st.error(
                            "YouTube refused the media request (HTTP 403). This may be a hosting "
                            "or YouTube request restriction; it is not necessarily a problem with "
                            "your video. Please upload the media file using the first tab."
                        )
                    else:
                        st.error(f"YouTube processing failed: {message}")

if st.session_state.original_segments is not None:
    st.divider()
    detected_name = st.session_state.detected_language_name or "Unknown"
    st.caption(f"Detected source language: **{detected_name}**")
    display_results(
        st.session_state.original_segments,
        f"Original Captions ({detected_name})",
        f"captions_original_{st.session_state.detected_language_code or 'und'}",
    )

    st.divider()
    st.subheader("🌐 Translate Captions")
    st.write("Keep the original captions, or translate them into another language.")
    target_options = list(LANGUAGES.keys())
    default_target_index = target_options.index("English") if "English" in target_options else 0
    target_language = st.selectbox(
        "Translate into",
        target_options,
        index=default_target_index,
        key="target_language",
    )
    if st.button("🌍 Translate Captions", type="primary", use_container_width=True):
        if target_language == detected_name:
            st.info("The selected target language matches the detected language. Choose another language if you need a translation.")
        else:
            api_key = get_openai_api_key()
            try:
                with st.spinner(f"Translating captions into {target_language}..."):
                    result = translate_segments(st.session_state.original_segments, target_language, api_key)
                st.session_state.translated_segments = result
                st.session_state.translation_target = target_language
                st.success(f"Translation complete: {target_language}")
            except Exception as exc:
                st.error(f"Translation failed: {exc}")

    if st.session_state.translated_segments is not None:
        target = st.session_state.translation_target or target_language
        target_code = safe_language_code(target)
        display_results(
            st.session_state.translated_segments,
            f"Translated Captions ({target})",
            f"captions_{target_code}",
        )
st.markdown(
    "<p style='text-align:center;color:#7b8494;font-size:.85rem;margin-top:28px;'>"
    "    </p>",
    unsafe_allow_html=True,
)

