import streamlit as st

import whisper

import yt_dlp as yt
import subprocess

import os 
import re

# global vars
user_agent_ID = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0"
language_options = {
    "Englisch": "en",
    "Deutsch": "de"
}
model = whisper.load_model("turbo")

def remove_special_characters(text):
    return re.sub(r'[^A-Za-z0-9]', '', text)

def get_video_title(url):
    ydl_opts = {
        'quiet': True,  # Suppresses download output
        'extract_flat': True , # Extracts metadata only,
        'http_headers': {
            'User-Agent': user_agent_ID  # Sets custom user-agent
        },
    }
    
    with yt.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('title', 'Title not found')


def download_audio_with_user_agent(url, output_path, filename, user_agent):
    ydl_opts = {
        'format': 'bestaudio/best',  # Ensures audio-only download
        'outtmpl': f'{output_path}/{filename}',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Extracts audio using FFmpeg
            'preferredcodec': 'mp3',      # Optional: converts audio to mp3
            'preferredquality': '192',    # Sets quality to 192 kbps
        }],
        'http_headers': {
            'User-Agent': user_agent_ID  # Sets custom user-agent
        }
    }
    with yt.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

st.title("Transkriptionsservice @ AA")

col1, col2 = st.columns(2, gap = "medium")

with col1: 
    url = st.text_input("Geben Sie eine URL ein", "")
    
with col2:
    selected_language  = st.selectbox("Wählen Sie eine Zielsprache aus:",
        options= language_options
        )
    
if url != "":
    if st.button("Herunterladen und transkribieren"):

        # get title
        video_title = get_video_title(url)

        file_name = remove_special_characters(video_title)
        output_dir = os.getcwd()
        # download audiostream
        st.write("Downloading <p> <b>", url, "</b> </p>", video_title, "</b> </p>", unsafe_allow_html=True)
            
        download_audio_with_user_agent(url, output_dir, file_name, user_agent_ID)
        
            
        st.write(f"Transkribiere...")
        path_to_file = os.path.join(output_dir, file_name+".mp3")

        target_lang = language_options[selected_language]
        result = model.transcribe(path_to_file, language = target_lang)
            
        st.write("Transkript:")

        st.write(result["text"])
        
        os.remove(f"{output_dir}/{file_name}")
        
            
        with open(f"{file_name}.txt", "w") as file:
            file.write(result["text"])
                
