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

"""


def text_to_audio(text: str, url: str):
    """
    Converts text to audio
    """
    data = {
        "prompt": text
    }

    response = requests.post(url, json=data)

    print(response)

    return response.content


if __name__ == "__main__":
    url = "https://ziik62hvohtk6obebrslkmreeq0rywbc.lambda-url.us-west-2.on.aws/"
    text = "Make a story about a robot"

    audio = text_to_audio(text, url)



    with open("robot_story.mp3", 'wb') as f:
        f.write(audio)