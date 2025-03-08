from flask import Flask, Response, stream_with_context, request, jsonify
import subprocess
import threading
import os 

app = Flask(__name__)

import requests
import json
import random 

# **Endpoints**
LAMBDA_URL = "https://ziik62hvohtk6obebrslkmreeq0rywbc.lambda-url.us-west-2.on.aws/"  # AWS Lambda (TTS + AI Response)
FASTAPI_URL = "http://44.244.151.238:8080/process-audio/"  # FastAPI Server for Video Processing

def generate_video_from_prompt(prompt):
    """ 
    1️⃣ Sends text to AWS Lambda for AI response + TTS 
    2️⃣ Sends the generated audio URL to FastAPI for video processing 
    3️⃣ Returns AI response, Audio URL, and Video URL
    """
    if not prompt:
        return "Please enter some text.", None, None
    
    # **Step 1: Call AWS Lambda for AI Response & TTS**
    try:
        print(f"🔹 Sending text to Lambda: {prompt}")
        lambda_response = requests.post(
            LAMBDA_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"prompt": prompt}),
            timeout=30
        )

        if lambda_response.status_code == 200:
            lambda_data = lambda_response.json()
            ai_response = lambda_data.get("text", "No AI response received")
            audio_url = lambda_data.get("audio_url")

            if not audio_url:
                return "Error: No audio URL received.", None, None

            print(f"✅ AI Response: {ai_response}")
            print(f"✅ Audio URL: {audio_url}")
        else:
            error_msg = f"❌ Lambda Error {lambda_response.status_code}: {lambda_response.text}"
            print(error_msg)
            return error_msg, None, None

    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Lambda request error: {str(e)}"
        print(error_msg)
        return error_msg, None, None

    # **Step 2: Call FastAPI to Process the Audio URL**
    try:
        print(f"🔹 Sending Audio URL to FastAPI: {audio_url}")
        fastapi_response = requests.get(
            FASTAPI_URL,
            params={"wav_url": audio_url},
            timeout=120
        )

        if fastapi_response.status_code == 200:
            fastapi_data = fastapi_response.json()
            video_url = fastapi_data.get("video_url")

            if not video_url:
                return "Error: No video URL received.", audio_url, None

            print(f"✅ Video URL (S3): {video_url}")
            return ai_response, audio_url, video_url
        else:
            error_msg = f"❌ FastAPI Error {fastapi_response.status_code}: {fastapi_response.text}"
            print(error_msg)
            return error_msg, audio_url, None

    except requests.exceptions.RequestException as e:
        error_msg = f"❌ FastAPI request error: {str(e)}"
        print(error_msg)
        return error_msg, audio_url, None


# Default video, but we can switch this anytime via /switch_video
video_source = "/home/ethan/clemson/DebugDungeon/example.mp4"

@app.route("/combined_feed")
def combined_feed():
    """
    Stream audio and video from the source as MP4 using FFmpeg.
    Whenever a new client hits this endpoint, it spawns an ffmpeg process
    reading the current `video_source`.
    """
    # Use global so we can modify it in /switch_video or /reset_video
    global video_source

    command = [
        "ffmpeg",
        "-re", 
        "-i", video_source,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "frag_keyframe+empty_moov",
        "-f", "mp4",
        "pipe:1"
    ]

    # Spawn an ffmpeg process for this client
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def generate():
        try:
            while True:
                data = process.stdout.read(1024)
                if not data:
                    break
                yield data
        finally:
            # Clean up if client disconnects
            process.kill()

    return Response(stream_with_context(generate()), mimetype="video/mp4")


@app.route("/switch_video", methods=["POST"])
def switch_video():
    """
    POST JSON like: {"text": "text to speak"}
    to switch the global video_source to a new path.
    """
    global video_source

    video_folder_path = "videos"

    data = request.get_json(force=True)
    text = data.get("text")

    print("/switch_video received text:", text)

    ai_response, audio_url, video_url = generate_video_from_prompt(text)

    print("Returned video URL:", video_url)

    # Download video url to the videos folder
    video_filename = str(random.randint(0, 1000000)) + ".mp4"
    video_path = f"{video_folder_path}/{video_filename}"
    video_file = requests.get(video_url)
    with open(video_path, "wb") as f:
        f.write(video_file.content)

    # new_path = data.get("path")

    # print("New path:", new_path)

    # if not new_path:
    #     return jsonify({"error": "No `path` provided."}), 400

    # # Update the global variable
    # video_source = new_path

    # All *future* requests to /combined_feed will play from new_path

    # Open the videos folder and choose the newest video by time
    newest_video = max([f"{video_folder_path}/{f}" for f in os.listdir(video_folder_path)], key=os.path.getctime)
    video_source = newest_video


    return jsonify({"message": f"Video source switched to {newest_video}"}), 200


@app.route("/reset_video", methods=["POST"])
def reset_video():
    """
    Reset video_source to the default path.
    Clients will need to reload to see the default again.
    """
    global video_source
    # You can store your "default" in a constant or do something else
    default_path = "/home/ethan/clemson/DebugDungeon/example.mp4"
    video_source = default_path
    return jsonify({"message": "Video source reset to default."}), 200


if __name__ == "__main__":
    # Threaded so multiple users can watch /combined_feed at once
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
