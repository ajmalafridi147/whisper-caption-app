import streamlit as st
import whisper
import tempfile
import os
import yt_dlp

# 1. Streamlit Page Configuration
st.set_page_config(
    page_title="AI Caption Studio",
    page_icon="🎙️",
    layout="wide"
)

# 2. CSS for Centering All Elements & Styling Download Buttons
st.markdown("""
    <style>
        /* Main Container Centering */
        .block-container {
            max-width: 800px;
            padding-top: 2rem;
            padding-bottom: 2rem;
            margin: 0 auto;
            text-align: center;
        }
        
        /* Headers Centering */
        h1, h2, h3, p {
            text-align: center !important;
        }
        
        /* File Uploader Centering */
        [data-testid="stFileUploader"] {
            width: 100%;
            margin: 0 auto;
        }
        
        /* Center Action Buttons */
        div.stButton > button {
            display: block;
            margin: 0 auto;
            width: 100%;
            max-width: 300px;
            background-color: #4f46e5;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 10px 20px;
        }
        
        /* Download Buttons Row */
        .download-container {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Helper Functions for Subtitle Formatting (SRT & VTT)
def format_time_srt(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def format_time_vtt(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

def generate_srt(segments):
    srt_text = ""
    for idx, seg in enumerate(segments, start=1):
        start = format_time_srt(seg['start'])
        end = format_time_srt(seg['end'])
        text = seg['text'].strip()
        srt_text += f"{idx}\n{start} --> {end}\n{text}\n\n"
    return srt_text

def generate_vtt(segments):
    vtt_text = "WEBVTT\n\n"
    for idx, seg in enumerate(segments, start=1):
        start = format_time_vtt(seg['start'])
        end = format_time_vtt(seg['end'])
        text = seg['text'].strip()
        vtt_text += f"{idx}\n{start} --> {end}\n{text}\n\n"
    return vtt_text

# 4. App UI Elements (Centered)
st.title("🎙️ AI Audio & Video Caption Generator")
st.write("Convert audio, video, or YouTube links into accurate captions & transcripts.")

# Load Whisper Model (Memory friendly tiny/base model)
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

model = load_whisper_model()

# Input Options (Tabs)
tab1, tab2 = st.tabs(["📁 File Upload", "🔗 YouTube Link"])

media_path = None

with tab1:
    uploaded_file = st.file_uploader("Upload Audio or Video File", type=["mp3", "wav", "mp4", "m4a", "mov"])
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded_file.read())
            media_path = tmp.name

with tab2:
    youtube_url = st.text_input("Paste YouTube Video URL")
    if youtube_url:
        if st.button("Fetch YouTube Audio"):
            with st.spinner("Downloading YouTube audio..."):
                try:
                    ydl_opts = {
                        'format': 'm4a/bestaudio/best',
                        'outtmpl': tempfile.mktemp(suffix='.m4a')
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(youtube_url, download=True)
                        media_path = ydl.prepare_filename(info)
                    st.success("YouTube audio extracted successfully!")
                except Exception as e:
                    st.error(f"Error fetching YouTube video: {e}")

# Process Button & Output Generation
if media_path and os.path.exists(media_path):
    if st.button("🚀 Generate Captions"):
        with st.spinner("Transcribing with OpenAI Whisper AI... Please wait..."):
            try:
                result = model.transcribe(media_path)
                st.success("Captions generated successfully!")
                
                # Show Transcribed Text Box
                st.subheader("Generated Transcription")
                st.text_area("", value=result['text'], height=200)
                
                # Generate Formats
                srt_data = generate_srt(result['segments'])
                vtt_data = generate_vtt(result['segments'])
                txt_data = result['text']
                
                # Download Buttons Section (Centered)
                st.subheader("📥 Download Captions for Platforms")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label="📄 Download .SRT (YouTube)",
                        data=srt_data,
                        file_name="subtitles.srt",
                        mime="text/plain"
                    )
                
                with col2:
                    st.download_button(
                        label="🌐 Download .VTT (Web)",
                        data=vtt_data,
                        file_name="subtitles.vtt",
                        mime="text/vtt"
                    )
                    
                with col3:
                    st.download_button(
                        label="📝 Download .TXT (Text)",
                        data=txt_data,
                        file_name="transcript.txt",
                        mime="text/plain"
                    )
                    
            except Exception as e:
                st.error(f"Error during transcription: {e}")
