import streamlit as st
from vosk import Model, KaldiRecognizer
import pyaudio
import json
from googleapiclient.discovery import build
import datetime
import isodate

# === API Key for YouTube ===
YOUTUBE_API_KEY = "AIzaSyABQliX2OILsdkGUIapDT1y6Wmxaj1_zcE"
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# === Load Vosk Model ===
model = Model(r"C:\Users\HP\Desktop\internship\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15")

# === Speech Recognition ===
def vosk_speech_to_text():
    recognizer = KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()
    st.write("🎤 Speak now...")
    while True:
        data = stream.read(4096)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            transcript = result.get("text", "").strip()
            return transcript

# === YouTube Search ===
def search_youtube_videos(query):
    published_after = (datetime.datetime.now() - datetime.timedelta(days=14)).isoformat("T") + "Z"
    search_response = youtube.search().list(q=query, part='snippet', maxResults=50, type='video', publishedAfter=published_after).execute()

    videos = []
    for item in search_response['items']:
        videos.append({
            'video_id': item['id']['videoId'],
            'title': item['snippet']['title']
        })
    return videos

# === Streamlit UI ===
st.title("YouTube Video Finder with Voice Search")
query = st.text_input("Enter a search query:")

if st.button("Search"):
    if query:
        results = search_youtube_videos(query)
        if results:
            for video in results[:10]:
                st.write(f"📌 **{video['title']}**")
                st.markdown(f"[Watch Video](https://www.youtube.com/watch?v={video['video_id']})")
        else:
            st.error("No results found.")
    else:
        st.error("Please enter a query.")

if st.button("🎤 Voice Search"):
    voice_query = vosk_speech_to_text()
    st.write("✅ You said:", voice_query)
    results = search_youtube_videos(voice_query)
    if results:
        for video in results[:10]:
            st.write(f"📌 **{video['title']}**")
            st.markdown(f"[Watch Video](https://www.youtube.com/watch?v={video['video_id']})")
    else:
        st.error("No results found.")