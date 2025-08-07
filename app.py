from flask import Flask, request, jsonify
import openai
import os
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

def get_transcript(youtube_url):
    import re
    match = re.search(r'(?:v=|youtu\.be/)([\w-]{11})', youtube_url)
    if not match:
        return None
    video_id = match.group(1)
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['vi', 'en'])
        transcript = " ".join([t['text'] for t in transcript_list])
        return transcript
    except Exception as e:
        print(e)
        return None

def summarize(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tóm tắt nội dung video YouTube thành văn bản ngắn gọn, rõ ràng, dễ hiểu cho người Việt."},
                {"role": "user", "content": text}
            ],
            max_tokens=500
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(e)
        return "Lỗi khi gọi API OpenAI"

@app.route('/api/summary', methods=['POST'])
def api_summary():
    data = request.json
    url = data.get('url')
    transcript = get_transcript(url)
    if not transcript:
        return jsonify({'error': 'Không lấy được transcript. Có thể video không hỗ trợ phụ đề.'}), 400
    summary = summarize(transcript)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)
