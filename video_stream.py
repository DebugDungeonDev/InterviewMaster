from flask import Flask, Response, stream_with_context, request, jsonify
import subprocess
import threading

app = Flask(__name__)

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
    POST JSON like: {"path": "/path/to/new_video.mp4"}
    to switch the global video_source to a new path.
    """
    global video_source
    data = request.get_json(force=True)
    new_path = data.get("path")

    print("New path:", new_path)

    if not new_path:
        return jsonify({"error": "No `path` provided."}), 400

    # Update the global variable
    video_source = new_path

    # All *future* requests to /combined_feed will play from new_path
    return jsonify({"message": f"Video source switched to {new_path}"}), 200


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
