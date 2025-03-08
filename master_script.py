import requests
import json

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

# **Feed Python user input to the function**
text = input("Enter a prompt: ")
ai_response, audio_url, video_url = generate_video_from_prompt(text)

print("\n🎬 **Final Output:**")
print(f"📜 AI Response: {ai_response}")
print(f"🔊 Audio URL: {audio_url}")
print(f"🎥 Video URL: {video_url}")  # ✅ Prints the S3 Video URL



    
