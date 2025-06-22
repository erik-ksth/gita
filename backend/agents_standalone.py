PROJECT_ID = "proven-reporter-463701-t8"

import base64
import json
import os
import google.auth
from google.auth.transport.requests import Request
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def send_request_to_google_api(api_endpoint, data=None):
    """
    Sends an HTTP request to a Google API endpoint.

    Args:
        api_endpoint: The URL of the Google API endpoint.
        data: (Optional) Dictionary of data to send in the request body (for POST, PUT, etc.).

    Returns:
        The response from the Google API.
    """

    # Get access token calling API
    try:
        creds, project = google.auth.default()
        auth_req = Request()
        creds.refresh(auth_req)
        access_token = creds.token
        print(f"Using project: {project}")
        print(f"Access token obtained successfully")
    except Exception as e:
        print(f"Authentication error: {e}")
        print("Please ensure you have proper Google Cloud authentication set up.")
        print("Options:")
        print("1. Run: gcloud auth application-default login")
        print("2. Set GOOGLE_APPLICATION_CREDENTIALS in .env file")
        raise

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    print(f"Sending request to: {api_endpoint}")
    print(f"Request data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(api_endpoint, headers=headers, json=data)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.status_code != 200:
            print(f"Error response: {response.text}")
            response.raise_for_status()

        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(
            f"Response content: {e.response.text if hasattr(e, 'response') else 'No response content'}"
        )
        raise
    except Exception as e:
        print(f"Request error: {e}")
        raise


def generate_music(request: dict):
    req = {"instances": [request], "parameters": {}}
    print(req)
    resp = send_request_to_google_api(music_model, req)
    return resp["predictions"]


def save_audio_to_file(preds, filename_prefix="generated_music"):
    """Save generated audio to files instead of playing them"""
    for i, pred in enumerate(preds):
        bytes_b64 = dict(pred)["bytesBase64Encoded"]
        decoded_audio_data = base64.b64decode(bytes_b64)

        filename = f"{filename_prefix}_{i+1}.wav"
        with open(filename, "wb") as f:
            f.write(decoded_audio_data)
        print(f"Audio saved to: {filename}")


music_model = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/lyria-002:predict"


if __name__ == "__main__":
    print("=== Google Music Generation Agent ===")

    # Example 1: Smooth jazz
    print("\n1. Generating smooth jazz...")
    prompt = "Smooth, atmospheric jazz. Moderate tempo, rich harmonies. Featuring mellow brass"
    negative_prompt = "fast"
    sample_count = 1

    try:
        music = generate_music(
            {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "sample_count": sample_count,
            }
        )
        save_audio_to_file(music, "smooth_jazz")
    except Exception as e:
        print(f"Error generating jazz: {e}")

    # Example 2: Dramatic dance symphony
    print("\n2. Generating dramatic dance symphony...")
    prompt = "Dramatic dance symphony"
    negative_prompt = ""
    seed = 111

    try:
        music = generate_music(
            {"prompt": prompt, "negative_prompt": negative_prompt, "seed": seed}
        )
        save_audio_to_file(music, "dramatic_symphony")
    except Exception as e:
        print(f"Error generating symphony: {e}")

    print("\n=== Generation complete ===")
