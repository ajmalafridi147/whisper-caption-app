import streamlit as st
import whisper
import yt_dlp
import os

# Page Configuration
st.set_page_config(page_title="AI Audio & Video Caption Generator", layout="centered")

# Hide Streamlit Default Header, Footer, and Menu (Branding Remove karne ke liye)
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🎙️ Free AI Audio & Video Caption Generator")
st.write("Generate accurate subtitles with timestamps for audio files and video links.")

@st.cache_resource
def load_model():
    return whisper.load_model("base")

with st.spinner("Loading AI Model..."):
    model = load_model()

media_url = st.text_input("Enter Video Link (YouTube, Reels, TikTok, etc.):", placeholder="https://...")
uploaded_file = st.file_uploader("Or Upload Audio File (.mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])

if st.button("Generate Captions", type="primary"):
    audio_path = None
    
    if media_url and media_url.strip() != "":
        st.info("Downloading media link (bypassing restrictions)...")
        
        # YouTube 403 Forbidden error bypass options
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
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(media_url, download=True)
                audio_path = "downloaded_audio.mp3"
        except Exception as e:
            st.error(f"Download Error: {str(e)}")

    elif uploaded_file is not None:
        audio_path = uploaded_file.name
        with open(audio_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    if audio_path:
        with st.spinner("Transcribing with Whisper... Please wait..."):
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

                st.success("Captions Generated Successfully!")
                st.text_area("Generated Subtitles:", value=formatted_text, height=350)

                if os.path.exists("downloaded_audio.mp3"):
                    os.remove("downloaded_audio.mp3")
            except Exception as e:
                st.error(f"Transcription Error: {str(e)}")
    else:
        st.warning("Please upload a file or paste a video link first.")

# Custom Clean Footer (Streamlit branding ki jagah apna footer)
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px;'>Powered by OpenAI Whisper • Built for Content Creators</p>", unsafe_allow_html=True)
