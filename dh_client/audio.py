"""
Utilities for grabbing the audo from the external servers
"""

import requests 


"""
Example CURL

curl -X POST \
  https://ziik62hvohtk6obebrslkmreeq0rywbc.lambda-url.us-west-2.on.aws/  \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "Make a story about a robot"}'


Audio URL example
"audio_url": "https://audio2faceaudiofiles.s3.us-west-2.amazonaws.com/tts_output_8554df11-8d09-4cb2-a79c-97f4f27c5369.377c6f34-03ef-4b16-820b-6d636ced1efe.pcm"

"""

def download_audio(url, output_path):
    custom_headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://example.com/"  # only if your bucket requires a referer
    }
    response = requests.get(url, stream=True, headers=custom_headers)

    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Downloaded successfully to {output_path}")
    else:
        print(f"Failed to download. Status code: {response.status_code}")
        print(f"Response text: {response.text}")  # Might help debug



def text_to_audio(text: str, url: str) -> bytes:
    """
    Converts text to audio by sending a request to the server and retrieving the audio file.

    :param text: The text prompt to be converted into audio.
    :param url: The endpoint URL for the text-to-speech service.
    :return: Audio file content in bytes.
    """
    data = {"prompt": text}

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an error if request fails
    except requests.RequestException as e:
        print(f"Error sending request: {e}")
        return None
    
    try:
        audio_url = response.json().get("audio_url")
        if not audio_url:
            print("No audio URL received.")
            return None
    except ValueError:
        print("Invalid JSON response received.")
        return None
    

    print("audio_url: ", audio_url)

    # Download the audio file
    download_audio(audio_url, "audio.mp3")




if __name__ == "__main__":
    url = "https://ziik62hvohtk6obebrslkmreeq0rywbc.lambda-url.us-west-2.on.aws/"
    text = "Make a story about a robot"

    text_to_audio(text, url)