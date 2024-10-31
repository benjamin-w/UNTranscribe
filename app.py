import streamlit as st

import whisper

from pytubefix import YouTube
from pytubefix.cli import on_progress

import os 
import re

def remove_special_characters(text):
    return re.sub(r'[^A-Za-z0-9]', '', text)

model = whisper.load_model("tiny")

st.title("Transcribe UN Speeches")

col1, col2 = st.columns(2, gap = "medium")

url = st.text_input("Geben Sie eine URL ein", "")
    
if url != "":
    if st.button("Herunterladen und transkribieren"):
            
        yt = YouTube(url, on_progress_callback = on_progress)    
        ys = yt.streams.get_audio_only()
        ys.download(mp3=True)
        
        st.write("Downloading <p> <b>", url, "</b> </p>", unsafe_allow_html=True)

        file_title_clean = remove_special_characters(yt.title)
        downloaded_file = f"{file_title_clean}.mp3"
            
        downloaded_file_path = os.path.join(os.getcwd(), downloaded_file)
            
        st.write(f"Started transcribing {file_title_clean}")
            
        result = model.transcribe(downloaded_file_path, language = "en")
            
        st.write("Done")
            
            
        with open(f"{yt.title}.txt", "w") as file:
            file.write(result["text"])
                
