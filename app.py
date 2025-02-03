import os
import requests
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

LINE_ACCESS_TOKEN = os.getenv("T9fIrAQgdM3i08pK+JeIVX/rXQlXCPHxaIBDwuyvXIscn6AF855eecPPGFzTzcUAdvI0YmniCP/+U+t4zM8klJUgDC/F53iUv/DIBzuiwSrC+lK/SHfJiKR/fhSZLiujK9fCBa2TTfCWI+Gf9UdEqwdB04t89/1O/w1cDnyilFU=")
LINE_NOTIFY_TOKEN = os.getenv("jW7L0b5mA8hPNMUyz9dmSgGcivrQKCGq3veqADtuENl")

def download_tiktok_video(url):
    output_file = "tiktok_video.mp4"
    command = ["yt-dlp", "-o", output_file, url]
    subprocess.run(command, check=True)
    return output_file

def send_to_line(video_path):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    files = {"videoFile": open(video_path, "rb")}
    data = {"message": "📢 คลิปจาก TikTok"}

    response = requests.post(url, headers=headers, data=data, files=files)
    return response.json()

def reply_message(reply_token, text):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {"Authorization": f"Bearer {LINE_ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {"replyToken": reply_token, "messages": [{"type": "text", "text": text}]}
    requests.post(url, headers=headers, json=data)

@app.route("/")
def home():
    return "Flask Webhook for LINE Bot is Running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        events = data.get("events", [])
        for event in events:
            if event.get("type") == "message":
                msg_text = event["message"]["text"]
                reply_token = event["replyToken"]
                if "tiktok.com" in msg_text:
                    reply_message(reply_token, "⏳ กำลังดาวน์โหลดวิดีโอ...")
                    video_path = download_tiktok_video(msg_text)
                    send_to_line(video_path)
                    os.remove(video_path)
                    reply_message(reply_token, "✅ วิดีโอถูกส่งไปที่ LINE Notify แล้ว!")
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
