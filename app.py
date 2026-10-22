import streamlit as st
import whisper
import yt_dlp
import os
import subprocess

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
    
    /* Additional clean up for bottom watermarks */
    footer:after {
        content: "";
        visibility: hidden;
        display: none;
    }
    
    /* Main Container Styling */
    .main {
        background-color: #f8fafc;
    }
    
    /* Hero Box Styling */
    .hero-box {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .hero-box h1 {
        color: white;
        font-size: 28px;
        margin-bottom: 10px;
    }
    .hero-box p {
        color: #e2e8f0;
        font-size: 15px;
    }

    /* Tip Box Styling */
    .tip-box {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 8px;
        color: #1e3a8a;
        font-size: 14px;
        margin-bottom: 20px;
    }
    
    /* Buttons Styling */
    .stButton>button {
        width: 100%;
        background-color: #4f46e5;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        color: white;
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
        <p>Generate professional timestamps & subtitles instantly using OpenAI Whisper.</p>
    </div>
""", unsafe_allow_html=True)

# --- Recommendation Notice ---
st.markdown("""
    <div class="tip-box">
        💡 <b>Pro Tip:</b> Direct <b>Audio File Upload (.mp3, .wav)</b> is the best, fastest, and 100% error-free way to generate captions. Video links from YouTube can sometimes face platform restrictions.
    </div>
""", unsafe_allow_html=True)

# --- Load Whisper Model ---
@st.cache_resource
def load_model():
    return whisper.load_model("base")

with st.spinner("Initializing AI Engine... Please wait..."):
    model = load_model()

# --- Method Selection Tabs ---
tab1, tab2 = st.tabs(["📁 Upload Audio File (Recommended)", "🔗 Paste Video Link"])

audio_path = None

# --- TAB 1: Audio Upload (Top & Preferred) ---
with tab1:
    st.subheader("Upload Audio File")
    uploaded_file = st.file_uploader("Choose an audio file (.mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])
    
    if uploaded_file is not None:
        audio_path = uploaded_file.name
        with open(audio_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Audio file loaded successfully!")

# --- TAB 2: URL Option (Alternative) ---
with tab2:
    st.subheader("Paste Media Link")
    media_url = st.text_input("Enter YouTube or Video Link:", placeholder="https://youtu.be/...")
    
    if media_url and media_url.strip() != "":
        st.info("Preparing to download media...")
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
            st.success("Video downloaded successfully!")
        except Exception as e:
            st.error(f"Download Error: {str(e)}")

# --- Transcription Action ---
if audio_path:
    st.markdown("---")
    if st.button("✨ Generate Subtitles Now", type="primary"):
        with st.spinner("🤖 AI is transcribing your media... (This may take a moment)"):
            try:
                result = model.transcribe(audio_path)
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

                st.success("🎉 Captions Generated Successfully!")
                
                # Output Textarea with easy copy feature
                st.text_area("Your Subtitles (Ready to Copy):", value=formatted_text, height=350)

                # Cleanup temporary file
                if os.path.exists("downloaded_audio.mp3"):
                    os.remove("downloaded_audio.mp3")
            except Exception as e:
                st.error(f"Transcription Error: {str(e)}")

# --- Professional Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px;'>Powered by OpenAI Whisper • Built for Content Creators</p>", unsafe_allow_html=True)
