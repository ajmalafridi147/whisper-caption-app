import streamlit as st
import whisper
import yt_dlp
import os
import subprocess
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Audio & Video Caption Generator",
    page_icon="🎙️",
    layout="centered"
)

# --- Aggressive Branding & Watermark Hider CSS ---
hide_streamlit_style = """
    <style>
    /* Hide Header, Footer, Menu, and Streamlit Watermarks */
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    .stDeployButton {visibility: hidden !important; display: none !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    
    /* Main Container Styling */
    .main {
        background-color: #f8fafc;
    }
    
    /* Hero Box Styling */
    .hero-box {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        padding: 25px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .hero-box h1 {
        color: white;
        font-size: 26px;
        margin-bottom: 8px;
    }
    .hero-box p {
        color: #e2e8f0;
        font-size: 14px;
        margin: 0;
    }

    /* Tip Box Styling */
    .tip-box {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 8px;
        color: #1e3a8a;
        font-size: 13.5px;
        margin-bottom: 20px;
    }
    
    /* Action Button Styling */
    .stButton>button {
        width: 100%;
        background-color: #4f46e5 !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3) !important;
        cursor: pointer !important;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #4338ca !important;
        box-shadow: 0 6px 15px rgba(67, 56, 202, 0.4) !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Auto Deno Setup for YouTube ---
@st.cache_resource
def setup_deno():
    try:
        subprocess.run("curl -fsSL https://deno.land/install.sh | sh -s v1.40.0 > /dev/null 2>&1", shell=True)
    except Exception:
        pass
    return True

setup_deno()

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
        💡 <b>Pro Tip:</b> Direct <b>Audio File Upload (.mp3, .wav)</b> is the fastest, most accurate, and 100% reliable method. Video links can sometimes fail due to platform anti-bot restrictions.
    </div>
""", unsafe_allow_html=True)

# --- Load Whisper Model ---
@st.cache_resource
def load_model():
    return whisper.load_model("base")

with st.spinner("Initializing AI Engine..."):
    model = load_model()

# --- Method Selection Tabs ---
tab1, tab2 = st.tabs(["📁 Method 1: Upload Audio File (Recommended)", "🔗 Method 2: Paste Video Link"])

uploaded_file = None
media_url = ""

# --- TAB 1: Audio Upload ---
with tab1:
    st.markdown("### Upload Audio File")
    uploaded_file = st.file_uploader("Select an audio file from your device (.mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])

# --- TAB 2: URL Option ---
with tab2:
    st.markdown("### Paste Video Link")
    media_url = st.text_input("Enter Video Link (YouTube, Shorts, etc.):", placeholder="https://www.youtube.com/watch?v=...")

st.markdown("---")

# --- VISIBLE PROCESS BUTTON ---
generate_btn = st.button("🚀 Generate Captions Now", type="primary")

if generate_btn:
    audio_path = None
    
    # Validation Check
    if not uploaded_file and not (media_url and media_url.strip()):
        st.warning("⚠️ Please upload an audio file OR enter a video link first before clicking the button!")
    else:
        # Progress UI Elements
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Handling Input (Audio File or Link Download)
        if uploaded_file is not None:
            status_text.info("📥 Processing uploaded audio file...")
            progress_bar.progress(25)
            
            audio_path = uploaded_file.name
            with open(audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            time.sleep(0.5)
            progress_bar.progress(50)
            
        elif media_url and media_url.strip() != "":
            status_text.info("⏳ Downloading audio from link... (Please wait)")
            progress_bar.progress(15)
            
            os.environ["PATH"] += os.pathsep + os.path.expanduser("~/.deno/bin")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloaded_audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'extractor_args': {
                    'youtube': {
                        'player_client': ['mweb', 'android']
                    }
                },
                'socket_timeout': 30,
                'geo_bypass': True,
                'nocheckcertificate': True,
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(media_url, download=True)
                    audio_path = "downloaded_audio.mp3"
                progress_bar.progress(50)
            except Exception as e:
                status_text.empty()
                progress_bar.empty()
                st.error(f"❌ Download Error: {str(e)}")

        # Step 2: Transcribing Media
        if audio_path and os.path.exists(audio_path):
            status_text.info("🤖 AI is listening & generating captions... Please do not close or refresh this page.")
            progress_bar.progress(70)
            
            try:
                result = model.transcribe(audio_path)
                progress_bar.progress(100)
                status_text.empty()
                
                formatted_text = ""
                if "segments" in result:
                    for seg in result["segments"]:
                        start = int(seg["start"])
                        end = int(seg["end"])
                        m_s, s_s = divmod(start, 60)
                        m_e, s_e = divmod(end, 60)
                        formatted_text += f"[{m_s:02d}:{s_s:02d} - {m_e:02d}:{s_e:02d}] {seg['text']}\n"
                else:
                    formatted_text = result["text"]

                # Success Output
                st.success("🎉 Captions Generated Successfully!")
                st.subheader("Your Subtitles (Select All & Copy):")
                st.text_area("Captions Output", value=formatted_text, height=350)

                # Clean temporary downloaded files
                if os.path.exists("downloaded_audio.mp3"):
                    os.remove("downloaded_audio.mp3")
                    
            except Exception as e:
                status_text.empty()
                progress_bar.empty()
                st.error(f"❌ Transcription Error: {str(e)}")

# --- Professional Clean Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px;'>Powered by OpenAI Whisper • Built for Content Creators</p>", unsafe_allow_html=True)
