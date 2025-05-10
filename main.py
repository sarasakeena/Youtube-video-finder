import datetime
import isodate
import logging
import sys
import json
import pyaudio
from vosk import Model, KaldiRecognizer
from googleapiclient.discovery import build

logging.basicConfig(stream=sys.stdout, level=logging.INFO, encoding="utf-8")
logger = logging.getLogger(__name__)

# === SET YOUR API KEY HERE ===
YOUTUBE_API_KEY = "AIzaSyABQliX2OILsdkGUIapDT1y6Wmxaj1_zcE"

# === YouTube Client ===
youtube = build('youtube', 'v3', developerKey="AIzaSyABQliX2OILsdkGUIapDT1y6Wmxaj1_zcE")

# === Vosk Speech-to-Text API for Voice Input ===
def vosk_speech_to_text(model_path=r"C:\Users\HP\Desktop\internship\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"):
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("🎤 Speak now...")
    while True:
        data = stream.read(4096)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            transcript = result.get("text", "").strip()
            print("✅ You said:", transcript)
            logger.info(f"User query: {transcript}")
            return transcript

# === Get user query (Voice or Text) ===
def get_user_query():
    mode = input("Choose input mode - (1) Voice, (2) Text: ").strip()
    if mode == "1":
        return vosk_speech_to_text(r"C:\Users\HP\Desktop\internship\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15")
    else:
        query = input("⌨️ Enter your query: ").strip()
        logger.info(f"User query: {query}")
        return query

# === Search YouTube ===
def search_youtube_videos(query):
    published_after = (datetime.datetime.now() - datetime.timedelta(days=14)).isoformat("T") + "Z"
    search_response = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=50,
        type='video',
        publishedAfter=published_after
    ).execute()

    videos = []
    for item in search_response['items']:
        videos.append({
            'video_id': item['id']['videoId'],
            'title': item['snippet']['title']
        })
        logger.info(f"Video ID: {item['id']['videoId']}, Title: {item['snippet']['title']}")
    return videos

# === Filter by duration ===
def filter_videos_by_duration(videos):
    filtered = []
    for chunk in [videos[i:i+10] for i in range(0, len(videos), 10)]:
        ids = ','.join([v['video_id'] for v in chunk])
        details = youtube.videos().list(part='contentDetails', id=ids).execute()

        for i, item in enumerate(details['items']):
            duration = isodate.parse_duration(item['contentDetails']['duration']).total_seconds()
            if 240 <= duration <= 1200:
                filtered.append(chunk[i])
                logger.info(f"Video ID: {chunk[i]['video_id']}, Title: {chunk[i]['title']}, Duration: {duration} seconds")
    return filtered[:20]

# === Simple title analysis (Keyword Matching) ===
def analyze_titles(videos, query):
    print("\n🧠 Selecting the best video based on keywords...")
    query_words = set(query.lower().split())

    best_video = None
    best_match_score = 0

    for video in videos:
        title_words = set(video['title'].lower().split())
        match_score = len(query_words.intersection(title_words))

        if match_score > best_match_score:
            best_match_score = match_score
            best_video = video

    if best_video:
        logger.info(f"Selected video: {best_video['title']}")
    return best_video

# === Main flow ===
def main():
    logger.info("Starting YouTube video finder...")
    query = get_user_query()
    if not query:
        print("❗ No query provided.")
        return

    print("\n🔍 Searching YouTube...")
    results = search_youtube_videos(query)
    if not results:
        print("❌ No results found.")
        return

    print("⏳ Filtering results...")
    filtered = filter_videos_by_duration(results)
    if not filtered:
        print("⚠️ No videos matched the duration/date filter.")
        return

    best_video = analyze_titles(filtered, query)

    if best_video:
        print("\n✅ Best Video Suggestion:")
        print("📌 Title:", best_video['title'])
        print("🔗 URL: https://www.youtube.com/watch?v=" + best_video['video_id'])
    else:
        print("❌ No suitable video found.")

# === Run the tool ===
if __name__ == "__main__":
    main()