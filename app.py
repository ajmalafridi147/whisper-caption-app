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

# --- Fully Centered & Professional UI Styling ---
custom_css = """
    <style>
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    .stDeployButton {visibility: hidden !important; display: none !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    
    /* Main App Background & Centering */
    .main .block-container {
        max-width: 850px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        margin: 0 auto;
    }
    
    /* Center all headers and paragraphs */
    h1, h2, h3, p, div {
        text-align: center;
    }
    
    /* Hero Box Styling */
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

    /* Tip Box Styling */
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
    
    /* Center File Uploader */
    [data-testid="stFileUploader"] {
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
    }
    [data-testid="stFileUploader"] section {
        text-align: center;
        margin: 0 auto;
    }

    /* Center Text Input */
    [data-testid="stTextInput"] {
        max-width: 600px;
        margin: 0 auto;
    }

    /* Center and Style Primary Action Buttons */
    .stButton>button {
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
    .stButton>button:hover {
        background-color: #4338ca !important;
        box-shadow: 0 6px 18px rgba(67, 56, 202, 0.4) !important;
    }

    /* Center Tabs */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

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
        💡 <b>Pro Tip:</b> Direct <b>Audio File Upload (.mp3, .wav)</b> is the fastest and 100% reliable method.
    </div>
""", unsafe_allow_html=True)

# --- Load Whisper Model ---
@st.cache_resource
def load_model():
    return whisper.load_model("base")

with st.spinner("Initializing AI Engine..."):
    model = load_model()

# --- Method Selection Tabs ---
tab1, tab2 = st.tabs(["📁 Method 1: Upload Audio File", "🔗 Method 2: Paste Video Link"])

uploaded_file = None
media_url = ""

# --- TAB 1: Audio Upload ---
with tab1:
    uploaded_file = st.file_uploader("Select an audio file from your device (.mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])

# --- TAB 2: URL Option ---
with tab2:
    media_url = st.text_input("Enter Video Link (YouTube, Shorts, etc.):", placeholder="https://www.youtube.com/watch?v=...")

st.markdown("---")

# --- VISIBLE PROCESS BUTTON ---
generate_btn = st.button("🚀 Generate Captions Now", type="primary")

if generate_btn:
    audio_path = None
    
    if not uploaded_file and not (media_url and media_url.strip()):
        st.warning("⚠️ Please upload an audio file OR enter a video link first!")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
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

        if audio_path and os.path.exists(audio_path):
            status_text.info("🤖 AI is listening & generating captions... Please wait.")
            progress_bar.progress(70)
            
            try:
                result = model.transcribe(audio_path)
                progress_bar.progress(100)
                status_text.empty()
                
                formatted_text = ""
                srt_text = "WEBVTT - Generated by AI Caption Studio\n\n"
                
                if "segments" in result:
                    for idx, seg in enumerate(result["segments"], start=1):
                        start = seg["start"]
                        end = seg["end"]
                        
                        # Format for display
                        start_int, end_int = int(start), int(end)
                        m_s, s_s = divmod(start_int, 60)
                        m_e, s_e = divmod(end_int, 60)
                        formatted_text += f"[{m_s:02d}:{s_s:02d} - {m_e:02d}:{s_e:02d}] {seg['text']}\n"
                        
                        # Format for SRT/VTT download
                        def fmt_time(t):
                            hrs = int(t // 3600)
                            mins = int((t % 3600) // 60)
                            secs = int(t % 60)
                            millis = int((t - int(t)) * 1000)
                            return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"
                        
                        srt_text += f"{idx}\n{fmt_time(start)} --> {fmt_time(end)}\n{seg['text'].strip()}\n\n"
                else:
                    formatted_text = result["text"]
                    srt_text = result["text"]

                st.success("🎉 Captions Generated Successfully!")
                st.subheader("Your Subtitles:")
                st.text_area("Captions Output", value=formatted_text, height=300)

                # Download Buttons for SRT Formats
                st.subheader("📥 Download Subtitles File")
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📄 Download .SRT File",
                        data=srt_text,
                        file_name="captions.srt",
                        mime="text/plain"
                    )
                with col2:
                    st.download_button(
                        label="📝 Download .TXT File",
                        data=formatted_text,
                        file_name="transcript.txt",
                        mime="text/plain"
                    )

                if os.path.exists("downloaded_audio.mp3"):
                    os.remove("downloaded_audio.mp3")
                    
            except Exception as e:
                status_text.empty()
                progress_bar.empty()
                st.error(f"❌ Transcription Error: {str(e)}")

# --- Professional Clean Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px;'>Powered by OpenAI Whisper • Built for Content Creators</p>", unsafe_allow_html=True)
