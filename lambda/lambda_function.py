import json
import boto3
import uuid

# Initialize AWS Clients with specific region
s3 = boto3.client("s3", region_name="us-west-2")
bedrock_client = boto3.client("bedrock-runtime", region_name="us-west-2")
polly_client = boto3.client("polly", region_name="us-west-2")

# Your S3 bucket name
S3_BUCKET_NAME = "audio2faceaudiofiles"

def lambda_handler(event, context):
    # Parse user input
    body = json.loads(event['body'])
    user_prompt = body.get("prompt", "")

    # 1) Call Amazon Bedrock (Llama 3)
    model_id = "arn:aws:bedrock:us-west-2:551916636156:inference-profile/us.meta.llama3-3-70b-instruct-v1:0"
    
    # Llama 3 format payload
    payload = {
        "prompt": user_prompt,
        "temperature": 1.0,
        "top_p": 0.9,
        "max_gen_len": 256
    }

    try:
        # Invoke Llama 3 on Bedrock
        bedrock_response = bedrock_client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )

        # Parse response
        response_body = json.loads(bedrock_response["body"].read())
        
        # Debug logging
        print("Bedrock response structure:", response_body)
        
        # Try different response formats
        if "generation" in response_body:
            model_answer = response_body["generation"]
        elif "completion" in response_body:
            model_answer = response_body["completion"]
        elif "content" in response_body and isinstance(response_body["content"], list):
            model_answer = response_body["content"][0]["text"]
        else:
            # Fallback
            print("Unknown response structure:", response_body)
            model_answer = str(response_body)

    except Exception as e:
        print(f"Error calling Bedrock: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    # 2) Call Amazon Polly for TTS
    try:
        # Generate a unique filename
        file_name = f"tts_output_{uuid.uuid4()}"
        
        # Use start_speech_synthesis_task to output directly to S3
        polly_response = polly_client.start_speech_synthesis_task(
            Text=model_answer,
            OutputFormat="mp3",  # Keep as MP3 for simplicity
            VoiceId="Joanna",
            OutputS3BucketName=S3_BUCKET_NAME,
            OutputS3KeyPrefix=file_name
        )
        
        # Get the S3 URI from the response
        output_uri = polly_response["SynthesisTask"]["OutputUri"]
        audio_url = output_uri

        # In the Polly section, add a delay or status check
        import time

        # After getting the task ID
        task_id = polly_response["SynthesisTask"]["TaskId"]

        # Optional: Wait for task to complete (for testing)
        status = "inProgress"
        while status == "inProgress":
            time.sleep(1)  # Wait 1 second
            status_response = polly_client.get_speech_synthesis_task(TaskId=task_id)
            status = status_response["SynthesisTask"]["TaskStatus"]
            if status == "failed":
                raise Exception("Polly task failed")
        
        # If you prefer a direct S3 URL format:
        # task_id = polly_response["SynthesisTask"]["TaskId"]
        # audio_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{file_name}.{task_id}.mp3"
        
    except Exception as e:
        print(f"Error calling Polly: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to generate speech", "details": str(e)})
        }

    # 3) Return the result
    response_payload = {
        "text": model_answer,
        "audio_url": audio_url,
        "format": "mp3"  # Indicate the format so your other service knows what to convert
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response_payload),
        "headers": {
            "Content-Type": "application/json"
        }
    }

# import json
# import boto3
# import base64
# import uuid
# from io import BytesIO
# from pydub import AudioSegment

# # Initialize AWS Clients
# s3 = boto3.client("s3")
# bedrock_client = boto3.client("bedrock-runtime")
# polly_client = boto3.client("polly")

# # Your S3 bucket name (Replace with your actual S3 bucket name)
# S3_BUCKET_NAME = "audio2faceaudiofiles"

# def lambda_handler(event, context):
#     # Parse user input
#     body = json.loads(event['body'])
#     user_prompt = body.get("prompt", "")

#     # 1) Call Amazon Bedrock (Claude 3.7 Sonnet)
#     model_id = "arn:aws:bedrock:us-west-2:551916636156:inference-profile/us.meta.llama3-3-70b-instruct-v1:0"

#     # Bedrock request payload
#     # Llama 3 format payload
#     payload = {
#         "prompt": user_prompt,
#         "temperature": 1.0,
#         "top_p": 0.9,
#         "max_gen_len": 256
#     }

#     try:
#         # Invoke Claude 3.7 Sonnet on Bedrock
#         bedrock_response = bedrock_client.invoke_model(
#             modelId=model_id,
#             contentType="application/json",
#             accept="application/json",
#             body=json.dumps(payload)
#         )

#         # Parse response
#         response_body = json.loads(bedrock_response["body"].read())
#         model_answer = response_body["content"][0]["text"]

#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"error": str(e)})
#         }

#     # 2) Call Amazon Polly for TTS
#     try:
#         polly_response = polly_client.synthesize_speech(
#             Text=model_answer,
#             OutputFormat="mp3",
#             VoiceId="Joanna"
#         )

#         # Read the MP3 audio stream
#         mp3_audio_stream = polly_response["AudioStream"].read()

#         # Convert MP3 to WAV using pydub
#         mp3_audio = AudioSegment.from_file(BytesIO(mp3_audio_stream), format="mp3")
#         wav_io = BytesIO()
#         mp3_audio.export(wav_io, format="wav")
#         wav_audio_bytes = wav_io.getvalue()

#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"error": "Failed to convert MP3 to WAV", "details": str(e)})
#         }

#     # 3) Store the WAV file in S3
#     try:
#         # Generate a unique filename
#         file_name = f"tts_output_{uuid.uuid4()}.wav"

#         # Upload to S3
#         s3.put_object(
#             Bucket=S3_BUCKET_NAME,
#             Key=file_name,
#             Body=wav_audio_bytes,
#             ContentType="audio/wav"
#         )

#         # Construct public URL for the file
#         audio_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{file_name}"

#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"error": "Failed to upload to S3", "details": str(e)})
#         }

#     # 4) Return the S3 URL instead of base64
#     response_payload = {
#         "text": model_answer,
#         "audio_url": audio_url  # Link to the WAV file
#     }

#     return {
#         "statusCode": 200,
#         "body": json.dumps(response_payload),
#         "headers": {
#             "Content-Type": "application/json"
#         }
#     }