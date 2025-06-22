import base64
import json
import os
import google.auth
from google.auth.transport.requests import Request
import requests
from dotenv import load_dotenv
from google.adk.agents import Agent
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_config import supabase, STORAGE_BUCKETS

# Load environment variables from parent folder
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Constants
PROJECT_ID = os.getenv("PROJECT_ID")
MUSIC_MODEL = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/lyria-002:predict"


def get_vision_analysis_from_supabase(video_id: str) -> str:
    """
    Fetch vision analysis result from Supabase database.

    Args:
        video_id: The UUID of the video

    Returns:
        The vision analysis result as a string
    """
    try:
        result = (
            supabase.table("videos")
            .select("vision_analysis, filename")
            .eq("id", video_id)
            .execute()
        )

        if not result.data:
            raise Exception(f"Video with ID {video_id} not found")

        video_data = result.data[0]
        vision_analysis = video_data.get("vision_analysis")
        filename = video_data.get("filename", "unknown")

        if not vision_analysis:
            print(
                f"Warning: No vision analysis found for video {video_id} ({filename})"
            )
            # Return a default prompt if no analysis is available
            return (
                "Ambient background music with gentle melodies and peaceful atmosphere"
            )

        print(
            f"Retrieved vision analysis for video {video_id} ({filename}): {vision_analysis[:100]}..."
        )
        return vision_analysis

    except Exception as e:
        print(f"Error fetching vision analysis from Supabase: {e}")
        raise


def upload_music_to_supabase(music_data: bytes, filename: str) -> str:
    """
    Upload generated music to Supabase storage.

    Args:
        music_data: The music file data as bytes
        filename: The filename for the music file

    Returns:
        The public URL of the uploaded music
    """
    try:
        # Upload music to Supabase storage
        result = supabase.storage.from_(STORAGE_BUCKETS["music"]).upload(
            filename, music_data, {"content-type": "audio/wav"}
        )

        if result:
            # Get public URL
            public_url = supabase.storage.from_(
                STORAGE_BUCKETS["music"]
            ).get_public_url(filename)
            print(f"Music uploaded to Supabase: {filename}")
            return public_url
        else:
            raise Exception("Failed to upload music to Supabase")

    except Exception as e:
        print(f"Error uploading music to Supabase: {e}")
        raise


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


def create_music_generation_record(
    video_id: str, vision_prompt: str = None, music_prompt: str = None
) -> str:
    """
    Create a new music generation record in the database.

    Args:
        video_id: The UUID of the video
        vision_prompt: The vision prompt used
        music_prompt: The custom music prompt (if any)

    Returns:
        The UUID of the created music generation record
    """
    try:
        result = (
            supabase.table("music_generations")
            .insert(
                {
                    "video_id": video_id,
                    "vision_prompt": vision_prompt,
                    "music_prompt": music_prompt,
                    "generation_status": "pending",
                }
            )
            .execute()
        )

        if result.data:
            generation_id = result.data[0]["id"]
            print(f"Created music generation record: {generation_id}")
            return generation_id
        else:
            raise Exception("Failed to create music generation record")

    except Exception as e:
        print(f"Error creating music generation record: {e}")
        raise


def update_music_generation_record(generation_id: str, **updates) -> None:
    """
    Update a music generation record with new data.

    Args:
        generation_id: The UUID of the music generation record
        **updates: Dictionary of fields to update
    """
    try:
        result = (
            supabase.table("music_generations")
            .update(updates)
            .eq("id", generation_id)
            .execute()
        )

        if result.data:
            print(f"Updated music generation record {generation_id}")
        else:
            print(f"Warning: Could not update music generation record {generation_id}")

    except Exception as e:
        print(f"Error updating music generation record: {e}")
        # Don't raise here to avoid breaking the workflow


def get_music_file_size(file_path: str) -> float:
    """
    Get the size of a music file in MB.

    Args:
        file_path: Path to the music file

    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)
    except Exception as e:
        print(f"Warning: Could not get file size for {file_path}: {e}")
        return 0.0


def generate_music_from_video_id(video_id: str, custom_music_prompt: str = None) -> str:
    """
    Generate music for a video using its stored vision analysis.

    Args:
        video_id: The UUID of the video
        custom_music_prompt: Optional custom music prompt to override vision analysis

    Returns:
        The Supabase URL of the generated music file
    """
    generation_id = None
    local_music_path = None

    try:
        print(f"Generating music for video ID: {video_id}")

        # Get the music prompt (either custom or from vision analysis)
        if custom_music_prompt:
            music_prompt = custom_music_prompt
            vision_prompt = None
            print(f"Using custom music prompt: {music_prompt[:100]}...")
        else:
            music_prompt = get_vision_analysis_from_supabase(video_id)
            vision_prompt = music_prompt
            print(f"Using vision analysis as music prompt")

        # Create music generation record
        generation_id = create_music_generation_record(
            video_id=video_id,
            vision_prompt=(
                vision_prompt[:1000] if vision_prompt else None
            ),  # Limit length
            music_prompt=custom_music_prompt,
        )

        # Update status to generating
        update_music_generation_record(generation_id, generation_status="generating")

        # Generate music using Lyria
        local_music_path = generate_music_with_lyria(
            prompt=music_prompt, negative_prompt="", sample_count=1
        )

        # Get file size
        music_file_size = get_music_file_size(local_music_path)

        # Read the generated music file
        with open(local_music_path, "rb") as f:
            music_data = f.read()

        # Create filename for Supabase storage
        music_filename = f"music_{video_id}_{generation_id}.wav"

        # Upload to Supabase
        music_url = upload_music_to_supabase(music_data, music_filename)

        # Update the music generation record with success
        update_music_generation_record(
            generation_id,
            music_file_path=music_url,
            music_file_size_mb=music_file_size,
            generation_status="completed",
        )

        print(f"Music generation completed for video {video_id}")
        return music_url

    except Exception as e:
        print(f"Error generating music for video {video_id}: {e}")

        # Update record with failure status
        if generation_id:
            update_music_generation_record(generation_id, generation_status="failed")

        raise

    finally:
        # Clean up local file
        if local_music_path and os.path.exists(local_music_path):
            try:
                os.remove(local_music_path)
                print(f"Cleaned up local music file: {local_music_path}")
            except Exception as cleanup_error:
                print(
                    f"Warning: Could not clean up local file {local_music_path}: {cleanup_error}"
                )


def get_music_generations_for_video(video_id: str) -> list:
    """
    Get all music generation records for a specific video.

    Args:
        video_id: The UUID of the video

    Returns:
        List of music generation records
    """
    try:
        result = (
            supabase.table("music_generations")
            .select("*")
            .eq("video_id", video_id)
            .order("created_at", desc=True)
            .execute()
        )

        if result.data:
            print(
                f"Found {len(result.data)} music generation records for video {video_id}"
            )
            return result.data
        else:
            print(f"No music generation records found for video {video_id}")
            return []

    except Exception as e:
        print(f"Error fetching music generations for video {video_id}: {e}")
        return []


def generate_music() -> str:
    """
    Legacy function for backward compatibility.
    Generates music based on the scene description from session state.

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
music_generator_agent = Agent(
    name="music_generator_agent",
    model="gemini-2.0-flash",
    description="An agent that generates music based on vision analysis from a video using Google's Lyria model.",
    instruction="""You are a music generation agent that creates music using Google's Lyria model based on video analysis.

    Your capabilities:
    1. Receive a video_id and fetch the vision analysis from the database
    2. Use the vision analysis as a music prompt for Lyria
    3. Generate music and upload it to Supabase storage
    4. Provide helpful feedback about the generation process

    When generating music:
    - Use the `generate_music_from_video_id` tool with the provided video_id
    - The vision analysis will be automatically fetched and used as the music prompt
    - The generated music will be uploaded to Supabase and local files cleaned up
    - Return the Supabase URL of the generated music

    Always respond clearly about what you're generating and provide the final URL when complete.
    """,
    tools=[
        generate_music_from_video_id,
        generate_music,
    ],  # Keep legacy function for compatibility
    output_key="generated_music_url",  # Store the music URL in session state
)
