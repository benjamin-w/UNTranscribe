import yt_dlp as yt
import subprocess


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import whisper

# Load Whisper 
model = whisper.load_model("small")


# Root window
window = tk.Tk()
window.title("UN Transcribe")
window.geometry('640x640')

# Style
style = ttk.Style(window)
# Set the theme with the theme_use method
style.theme_use('aqua')  # put the theme name here, that you want to use


#title
title_label = ttk.Label(master = window, text = "UN Web TV Transkriptor", font = 'Calibri 24 bold')
title_label.pack()

# list audiostreams
def handle_find_streams():
    print("find audio streams")
    explainer["text"] = "Audiostream für Transkription auswählen"
    video_url = url_entry.get()

    if not video_url:
        messagebox.showerror("Error", "Bitte geben Sie eine gültige URL ein")
        return
    
    try:
        list_audio_streams_command = [
            "yt-dlp",
            "-F",
            video_url,
            "--user-agent",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0"]
        
        result = subprocess.run(list_audio_streams_command, 
                            capture_output=True,
                            text=True,
                            check=True)
        # filter formats
        formats = []
        for line in result.stdout.splitlines():
            if "audio only" in line:
                formats.append(line)

        # Clear the Listbox and add new formats
        audio_listbox.delete(0, tk.END)
        for fmt in formats:
            audio_listbox.insert(tk.END, fmt)

        
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to get audio formats:\n{e}")
    
def  download_selected_audio():
    # Get the selected line from the Listbox
    print("download clicked\n")
    selection = audio_listbox.curselection()
    if not selection:
        return  # No selection, so nothing to do

    selected_format = audio_listbox.get(selection[0])
    
    # Extract the format ID (assuming it's the first field in the selected line)
    format_id = selected_format.split()[0]
    
    # Get the URL from the Entry widget
    url = url_entry.get()
    
    try:
        asset_id = url.split('/')[-1]
        # Run yt-dlp to download the selected audio format
        subprocess.run(
            ["yt-dlp", "-f", format_id, url, "--user-agent",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0",
              "-o", asset_id+".mp4"],
            check=True)
        

        transcribe_audio(asset_id)
    
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to download audio format {format_id}:\n{e}")

def transcribe_audio(asset_id):
    print("transcribe audio")
    filename = asset_id+".mp4"
    result = model.transcribe(filename, language="en")
    with open(asset_id+".txt", "w") as file:
        file.write(result["text"])
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, result["text"])




# Explanation
explainer = tk.Label(text="Video URL hier eingeben")
explainer.pack()



#input field
input_frame = ttk.Frame(master = window)
url_entry = ttk.Entry(master = input_frame, width=50)
button = ttk.Button(master = input_frame, text = "Verfügbare Audiostreams finden", command = handle_find_streams)

# button.bind("<Button-1>", handle_find_streams)

# Listbox to display audio formats
audio_listbox = tk.Listbox(window, width=100, height=10)

# Selecting Audiostream
#audio_listbox.bind("<<ListboxSelect>>", download_selected_audio)

download_button = tk.Button(window, text="Ausgewählten Audio Track transkribieren", command=download_selected_audio)

text_widget = tk.Text(window, width=100, height=30)




# Insert text into the Text widget


url_entry.pack()
button.pack()
input_frame.pack()
audio_listbox.pack(pady=5)
download_button.pack(pady=10)
text_widget.pack(pady=10)

scrollbar = tk.Scrollbar(input_frame, orient="vertical", command=text_widget.yview)
scrollbar.pack(side="right", fill="y")
text_widget.config(yscrollcommand=scrollbar.set)

window.mainloop()

