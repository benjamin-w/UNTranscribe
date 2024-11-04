import streamlit as st

import whisper

import yt_dlp as yt
import subprocess
import random

from mutagen.mp3 import MP3


import os 
import re

# global vars
user_agent_list = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0"]#,
# "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
# "Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18",
# "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
# "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/116.0.0.0 Mobile/15E148 Safari/604.1",
# "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
# "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2; rv:118.0) Gecko/20100101 Firefox/118.0",
# "Mozilla/5.0 (Android 11; Mobile; rv:118.0) Gecko/118.0 Firefox/118.0",
# "Safari/537.36 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/14.0",
# "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"]

language_options = {
    "Originalsprache transkribieren": "orig",
    "Transkribieren & Englisch übersetzen": "en",
    "Transkribieren & Deutsch übersetzen": "de"
}


model = whisper.load_model("small")

def get_user_agent_ID():
    ua_list_length = len(user_agent_list)
    return user_agent_list[random.randint(0, ua_list_length-1)]

def remove_special_characters(text):
    return re.sub(r'[^A-Za-z0-9]', '', text)

def get_video_info(url):
    ydl_opts = {
        'quiet': True,  # Suppresses download output
        'extract_flat': True , # Extracts metadata only,
        'verbose': True,
        'http_headers': {
            'User-Agent': get_user_agent_ID()  # Sets custom user-agent
        },
    }
    
    with yt.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('title', 'Title not found')


def download_audio_stream(url, output_path, filename):
    ydl_opts = {
        'format': 'bestaudio/best',  # Ensures audio-only download
        'outtmpl': f'{output_path}/{filename}',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Extracts audio using FFmpeg
            'preferredcodec': 'mp3',      # Optional: converts audio to mp3
            'preferredquality': '192',    # Sets quality to 192 kbps
        }],
        'http_headers': {
            'User-Agent': get_user_agent_ID()  # Sets custom user-agent
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
        options = language_options
        )
    
with st.expander("Wie funktioniert's?"):
    st.write('''
        Mithilfe dieser Seite können Sie sich Videos aus dem Internet transkribieren und übersetzen lassen. 
             Fügen Sie dazu die URL des gewünschten Videos in das linke Feld. Wählen Sie anschließend im rechten Menü aus, ob Sie das Video in der 
            Originalsprache transkribiert haben möchten, oder die Transkription zusätzlich in Englisch oder Deutsch übersetzt haben möchten. Das System erkennt und transkribiert die 100 meistgesprochenen Sprachen, wenn auch mit unterschiedlicher Genauigkeit.
            Wichtig: Sowohl die Transkription als auch die Übersetzung ist maschinell erstellt und kann daher Fehler enthalten.
    ''')
    
    
if url != "":
    if st.button("Herunterladen und transkribieren"):
        st.write("Informationen werden geladen...")
        video_title = get_video_info(url)

        st.write(url, "</b> </p> <em>", video_title, "</em> </b> </p>", unsafe_allow_html=True)   

        asset_id = url.split('/')[-1]
        file_name = remove_special_characters(asset_id) #remove_special_characters(video_title)
        output_dir = os.getcwd()
        
        st.write("Tonspur wird heruntergeladen...", unsafe_allow_html=True)     

        download_audio_stream(url, output_dir, file_name)     
    
        st.write(f"Transkribiere...")
        path_to_file = os.path.join(output_dir, file_name+".mp3")

        target_lang = language_options[selected_language]

        if target_lang == "orig":
            result = model.transcribe(path_to_file, task = "transcribe")    
        else:
            result = model.transcribe(path_to_file, language = target_lang)    

        st.write(result["text"])
        
        os.remove(f"{output_dir}/{file_name}")
                   
        with open(f"{file_name}.txt", "w") as file:
            file.write(result["text"])
                