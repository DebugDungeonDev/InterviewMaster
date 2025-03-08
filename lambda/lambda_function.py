import json
import boto3
import uuid
import time
import wave
import os

# AWS Clients
s3 = boto3.client("s3", region_name="us-west-2")
polly_client = boto3.client("polly", region_name="us-west-2")
bedrock_client = boto3.client("bedrock-runtime", region_name="us-west-2")

# Define Buckets
PCM_BUCKET = "pcmbucket123"  # 🔹 Store raw PCM files
WAV_BUCKET = "audio2faceaudiofiles"  # 🔹 Store converted WAV files

def lambda_handler(event, context):
    body = json.loads(event['body'])
    user_prompt = body.get("prompt", "")

    # 1) Call Amazon Bedrock (Llama 3) to Generate Text Response
    model_id = "arn:aws:bedrock:us-west-2:551916636156:inference-profile/us.meta.llama3-3-70b-instruct-v1:0"

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

        # Extract model response text
        if "generation" in response_body:
            model_answer = response_body["generation"]
        elif "completion" in response_body:
            model_answer = response_body["completion"]
        elif "content" in response_body and isinstance(response_body["content"], list):
            model_answer = response_body["content"][0]["text"]
        else:
            print("Unknown response structure:", response_body)
            model_answer = str(response_body)

    except Exception as e:
        print(f"Error calling Bedrock: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "LLM inference failed", "details": str(e)})
        }

    # 2) Call Amazon Polly for TTS (PCM format)
    try:
        file_base = f"tts_output_{uuid.uuid4()}"

        polly_response = polly_client.start_speech_synthesis_task(
            Text=model_answer,
            OutputFormat="pcm",
            SampleRate="16000",
            VoiceId="Joanna",
            OutputS3BucketName=PCM_BUCKET,  # 🔹 Store PCM in separate bucket
            OutputS3KeyPrefix=file_base
        )

        task_id = polly_response["SynthesisTask"]["TaskId"]
        status = "inProgress"

        while status == "inProgress":
            time.sleep(3)  # Wait 3 seconds before checking status
            status_response = polly_client.get_speech_synthesis_task(TaskId=task_id)
            status = status_response["SynthesisTask"]["TaskStatus"]
            if status == "failed":
                raise Exception("Polly task failed")

        # Construct the PCM file key
        pcm_key = f"{file_base}.{task_id}.pcm"

        # 🔹 Wait for PCM file to appear in S3
        max_wait_time = 30
        elapsed_time = 0
        while elapsed_time < max_wait_time:
            try:
                s3.head_object(Bucket=PCM_BUCKET, Key=pcm_key)
                print(f"PCM file found in {PCM_BUCKET}: {pcm_key}")
                break
            except s3.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print(f"PCM file not found yet, retrying... {elapsed_time} sec")
                    time.sleep(2)
                    elapsed_time += 2
                else:
                    raise e

        if elapsed_time >= max_wait_time:
            raise Exception(f"PCM file did not appear in {PCM_BUCKET} within {max_wait_time} seconds")

        # ✅ Download PCM file from `pcmbucket123`
        local_pcm_path = f"/tmp/{file_base}.pcm"
        local_wav_path = f"/tmp/{file_base}.wav"

        s3.download_file(PCM_BUCKET, pcm_key, local_pcm_path)
        print(f"Downloaded PCM file to: {local_pcm_path}")

        # ✅ Convert PCM to WAV
        convert_pcm_to_wav(local_pcm_path, local_wav_path)
        print(f"Converted WAV file saved at: {local_wav_path}")

        # ✅ Upload WAV file to `audio2faceaudiofiles`
        wav_key = f"{file_base}.wav"
        s3.upload_file(local_wav_path, WAV_BUCKET, wav_key)
        print(f"Uploaded WAV file to {WAV_BUCKET}: {wav_key}")

        # 🔹 Ensure WAV file was successfully uploaded
        s3.head_object(Bucket=WAV_BUCKET, Key=wav_key)
        print(f"Confirmed WAV file in S3: {wav_key}")

        # Generate WAV file URL
        wav_url = f"https://{WAV_BUCKET}.s3.{s3.meta.region_name}.amazonaws.com/{wav_key}"

    except Exception as e:
        print(f"Error processing TTS: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": "TTS processing failed", "details": str(e)})}

    # 3) Return the result
    return {
        "statusCode": 200,
        "body": json.dumps({
            "text": model_answer,
            "audio_url": wav_url,
            "format": "wav",
            "sample_rate": "16000"
        }),
        "headers": {"Content-Type": "application/json"}
    }

def convert_pcm_to_wav(pcm_path, wav_path):
    """Convert raw PCM data to WAV format"""
    try:
        with open(pcm_path, 'rb') as pcm_file:
            pcm_data = pcm_file.read()

        with wave.open(wav_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit PCM
            wav_file.setframerate(16000)  # 16kHz sample rate
            wav_file.writeframes(pcm_data)
        print(f"Converted PCM to WAV successfully: {wav_path}")

    except Exception as e:
        print(f"Error converting PCM to WAV: {str(e)}")
        raise e









# import json
# import boto3
# import uuid
# import time

# # AWS Clients - adding region for consistency
# s3 = boto3.client("s3", region_name="us-west-2")
# polly_client = boto3.client("polly", region_name="us-west-2")
# bedrock_client = boto3.client("bedrock-runtime", region_name="us-west-2")

# # Your S3 bucket
# S3_BUCKET_NAME = "audio2faceaudiofiles"

# def lambda_handler(event, context):
#     # Parse input
#     body = json.loads(event['body'])
#     user_prompt = body.get("prompt", "")

#     # 1) Call Amazon Bedrock (Llama 3) to Generate Response
#     model_id = "arn:aws:bedrock:us-west-2:551916636156:inference-profile/us.meta.llama3-3-70b-instruct-v1:0"
    
#     # Construct the Llama 3 payload
#     payload = {
#         "prompt": user_prompt,
#         "temperature": 1.0,
#         "top_p": 0.9,
#         "max_gen_len": 256
#     }

#     try:
#         # Invoke Llama 3 on Bedrock
#         bedrock_response = bedrock_client.invoke_model(
#             modelId=model_id,
#             contentType="application/json",
#             accept="application/json",
#             body=json.dumps(payload)
#         )

#         # Parse response
#         response_body = json.loads(bedrock_response["body"].read())
        
#         # Extract model response text
#         if "generation" in response_body:
#             model_answer = response_body["generation"]
#         elif "completion" in response_body:
#             model_answer = response_body["completion"]
#         elif "content" in response_body and isinstance(response_body["content"], list):
#             model_answer = response_body["content"][0]["text"]
#         else:
#             print("Unknown response structure:", response_body)
#             model_answer = str(response_body)

#     except Exception as e:
#         print(f"Error calling Bedrock: {str(e)}")
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"error": "LLM inference failed", "details": str(e)})
#         }

#     # 2) Call Amazon Polly for TTS (PCM format)
#     try:
#         file_base = f"tts_output_{uuid.uuid4()}"
        
#         polly_response = polly_client.start_speech_synthesis_task(
#             Text=model_answer,
#             OutputFormat="pcm",  # PCM is raw audio
#             SampleRate="16000",
#             VoiceId="Joanna",
#             OutputS3BucketName=S3_BUCKET_NAME,
#             OutputS3KeyPrefix=file_base
#         )
        
#         # Get Task ID and URI
#         task_id = polly_response["SynthesisTask"]["TaskId"]
#         status = "inProgress"

#         while status == "inProgress":
#             time.sleep(1)
#             status_response = polly_client.get_speech_synthesis_task(TaskId=task_id)
#             status = status_response["SynthesisTask"]["TaskStatus"]
#             if status == "failed":
#                 raise Exception("Polly task failed")
        
#         # Construct the PCM file key
#         pcm_key = f"{file_base}.{task_id}.pcm"
        
#         # Generate a direct URL to the PCM file
#         pcm_url = f"https://{S3_BUCKET_NAME}.s3.{s3.meta.region_name}.amazonaws.com/{pcm_key}"

#     except Exception as e:
#         print(f"Error calling Polly: {str(e)}")
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"error": "TTS synthesis failed", "details": str(e)})
#         }

#     # 3) Return the result
#     return {
#         "statusCode": 200,
#         "body": json.dumps({
#             "text": model_answer,
#             "audio_url": pcm_url,
#             "format": "pcm",
#             "sample_rate": "16000"
#         }),
#         "headers": {"Content-Type": "application/json"}
#     }


