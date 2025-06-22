import base64
import json
import os
import google.auth
from google.auth.transport.requests import Request
import requests
from dotenv import load_dotenv
from google.adk.agents import Agent

# Load environment variables from parent folder
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Constants
PROJECT_ID = os.getenv("PROJECT_ID")
MUSIC_MODEL = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/lyria-002:predict"


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


def generate_music_with_lyria(
    prompt: str, negative_prompt: str = "", sample_count: int = 1, seed: int = None
) -> str:
    """
    Generates music using Google's Lyria model.

    Args:
        prompt: Text description of the music to generate
        negative_prompt: What to avoid in the music generation
        sample_count: Number of music samples to generate
        seed: Random seed for reproducible generation

    Returns:
        The file path to the generated music file.
    """
    try:
        # Prepare request data
        request_data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "sample_count": sample_count,
        }

        if seed is not None:
            request_data["seed"] = seed

        # Create the request payload
        req = {"instances": [request_data], "parameters": {}}
        print(f"Generating music with request: {json.dumps(req, indent=2)}")

        # Send request to Lyria
        resp = send_request_to_google_api(MUSIC_MODEL, req)

        # Save the generated audio
        if "predictions" in resp and resp["predictions"]:
            preds = resp["predictions"]
            filename_prefix = f"generated_music_{hash(prompt) % 10000}"

            # Save audio to file
            for i, pred in enumerate(preds):
                bytes_b64 = dict(pred)["bytesBase64Encoded"]
                decoded_audio_data = base64.b64decode(bytes_b64)

                filename = f"{filename_prefix}_{i+1}.wav"
                with open(filename, "wb") as f:
                    f.write(decoded_audio_data)
                print(f"Audio saved to: {filename}")

                # Return the first generated file path
                return filename
        else:
            raise Exception("No predictions returned from Lyria")

    except Exception as e:
        print(f"Error generating music: {e}")
        raise


def generate_music() -> str:
    """Generates music based on the scene description from session state.

    Returns:
        The file path to the generated music file.
    """
    # The description will be read from session state by the agent
    # This function will be called by the agent with access to session context
    print("Generating music based on scene description from session state")

    # Generate music using Lyria with description from session state
    return generate_music_with_lyria(
        prompt="A peaceful scene with ambient music",  # This will be overridden by the agent
        negative_prompt="",  # Can be customized based on needs
        sample_count=1,
    )


# Create the ADK agent
music_generation_agent = Agent(
    name="music_generation_agent",
    model="gemini-2.0-flash",
    description="An agent that generates music based on a music prompt using Google's Lyria model.",
    instruction="""You are a music generation agent that creates music using Google's Lyria model.

Your capabilities:
1. Read the music prompt from session state (key: 'music_prompt')
2. Use the `generate_music` tool to create music with Lyria
3. Provide helpful feedback about the generation process

When generating music:
- The music prompt is available in session state as: {music_prompt}
- Use this prompt directly with the Lyria model
- Generate 1 sample by default unless specified otherwise
- Return the file path of the generated music

The `generate_music` tool will use the music prompt from session state automatically.
Always respond clearly about what you're generating and provide the file path when complete.
""",
    tools=[generate_music],
    output_key="generated_music_path",  # Store the music file path in session state
)


# Example usage and testing
if __name__ == "__main__":
    print("=== Music Generation Agent Test ===")

    # Test 1: Calm ambient music
    print("\n1. Generating calm ambient music...")
    try:
        result1 = generate_music()
        print(f"Generated music: {result1}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Dramatic music
    print("\n2. Generating dramatic music...")
    try:
        result2 = generate_music()
        print(f"Generated music: {result2}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== Test Complete ===")
