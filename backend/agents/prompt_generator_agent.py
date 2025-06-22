import datetime
import os
import requests
import base64
from typing import List
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Groq configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def download_image_from_url(image_url: str) -> bytes:
    """Download image from URL and return as bytes.

    Args:
        image_url: The URL of the image to download

    Returns:
        Image data as bytes
    """
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error downloading image from {image_url}: {e}")
        raise


def encode_image_to_base64(image_bytes: bytes) -> str:
    """Encode image bytes to base64 string.

    Args:
        image_bytes: Image data as bytes

    Returns:
        Base64 encoded string
    """
    return base64.b64encode(image_bytes).decode("utf-8")


def send_images_to_groq(image_urls: List[str], custom_prompt: str = None) -> str:
    """Send images and prompt to Groq API for analysis.

    Args:
        image_urls: List of image URLs to analyze
        custom_prompt: Custom prompt for analysis

    Returns:
        Analysis result from Groq
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set")

    # Default prompt if none provided
    if not custom_prompt:
        custom_prompt = """Analyze these video frames and generate a detailed, specific prompt for background music generation using Lyria. Follow the Lyria music generation prompt guide format.

    Focus on:
    - Visual mood and atmosphere
    - Movement and energy in the scene
    - Color palette and lighting
    - Emotional tone
    - Suitable music style and instruments

    Generate ONLY the music prompt, no additional text or explanations.

    Example format: "Dark Hybrid Film Score, Los Angeles, Studio recording, ominous and relentless. Pristine contemporary Instrumental, recorded live London, Dark Trailer Music. A blend of driving percussive synths, distorted orchestral elements, and filmic pulse textures, with instruments such as synths, distorted strings, brass, and hybrid percussion, and a cinematic approach, featuring pulsing rhythms, dissonant harmonies, and a sense of impending dread, evoking a tense and foreboding atmosphere"
    """

    try:
        # Prepare images for Groq
        image_contents = []
        for i, image_url in enumerate(image_urls):
            try:
                print(f"Downloading image {i+1}/{len(image_urls)}: {image_url}")
                image_bytes = download_image_from_url(image_url)
                image_b64 = encode_image_to_base64(image_bytes)

                image_contents.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    }
                )
                print(f"Successfully processed image {i+1}")

            except Exception as e:
                print(f"Error processing image {i+1}: {e}")
                continue

        if not image_contents:
            raise Exception("No valid images could be processed")

        # Prepare the request for Groq
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        # Create message with text prompt + images
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": custom_prompt}] + image_contents,
            }
        ]

        data = {
            "model": "meta-llama/llama-4-maverick-17b-128e-instruct",  # Updated to current Groq vision model
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7,
        }

        print(f"Sending {len(image_contents)} images to Groq for analysis...")

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        )

        print(f"Groq API response status: {response.status_code}")

        if response.status_code != 200:
            print(f"Groq API error response: {response.text}")
            response.raise_for_status()

        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            analysis_result = result["choices"][0]["message"]["content"]
            print(f"Groq analysis completed successfully")
            return analysis_result.strip()
        else:
            raise Exception("No response from Groq")

    except Exception as e:
        print(f"Error sending images to Groq: {e}")
        raise


def analyze_video_frames_from_supabase(video_id: str, custom_prompt: str = None) -> str:
    """Analyzes video frames from Supabase using Groq and generates a music prompt.

    Args:
        video_id: The UUID of the video to analyze frames for.
        custom_prompt: Optional custom prompt for the analysis.

    Returns:
        A string containing the music generation prompt from Groq.
    """
    try:
        print(f"Analyzing frames for video ID: {video_id}")

        # Fetch frame data from Supabase
        frame_paths = get_frames_from_supabase(video_id)

        if not frame_paths:
            print("No frames found for this video")
            return "Neutral background music with subtle ambient tones."

        print(f"Found {len(frame_paths)} frames, sending to Groq for analysis...")

        # Send images to Groq for actual analysis
        analysis_result = send_images_to_groq(frame_paths, custom_prompt)

        print(f"Groq analysis completed successfully")
        return analysis_result

    except Exception as e:
        print(f"Error analyzing video frames: {e}")
        # Return fallback prompt if analysis fails
        return "Calm ambient music with peaceful undertones and gentle atmospheric textures."


def get_frames_from_supabase(video_id: str) -> List[str]:
    """Retrieves frame paths from Supabase for a given video ID.

    Args:
        video_id: The UUID of the video to get frames for.

    Returns:
        A list of frame file paths stored in Supabase.
    """
    try:
        # Query Supabase for frames associated with the video
        response = (
            supabase.table("frames")
            .select("file_path")
            .eq("video_id", video_id)
            .order("frame_number")
            .execute()
        )

        if response.data:
            frame_paths = [item["file_path"] for item in response.data]
            print(
                f"Retrieved {len(frame_paths)} frame paths from Supabase for video {video_id}"
            )
            return frame_paths
        else:
            print(f"No frames found for video ID: {video_id}")
            return []

    except Exception as e:
        print(f"Error retrieving frames from Supabase: {e}")
        return []


# Legacy function for backward compatibility
def analyze_images_from_supabase(image_paths: List[str]) -> str:
    """Legacy function - analyzes images from provided paths.

    This function is kept for backward compatibility but is deprecated.
    Use analyze_video_frames_from_supabase() with video_id instead.

    Args:
        image_paths: A list of image paths stored in Supabase.

    Returns:
        A string containing the music generation prompt.
    """
    try:
        print(f"[DEPRECATED] Analyzing {len(image_paths)} images from provided paths")
        print(
            "Consider using analyze_video_frames_from_supabase() with video_id instead"
        )

        # Use the new Groq integration for legacy function too
        if image_paths:
            return send_images_to_groq(image_paths)
        else:
            return "Neutral background music with subtle ambient tones."

    except Exception as e:
        print(f"Error analyzing images: {e}")
        return "Calm ambient music with peaceful undertones."


prompt_generator_agent = Agent(
    name="prompt_generator_agent",
    model=LiteLlm(model="groq/meta-llama/llama-4-maverick-17b-128e-instruct"),
    description="An agent that analyzes video frames from Supabase and generates music prompts using Groq.",
    instruction="""You are an expert LLM prompt engineer. Your TASK is to generate ONLY a detailed, specific prompt for background music generation using Lyria. When crafting the prompt, make sure to strictly adhere to the Lyria music generation prompt guide (https://cloud.google.com/vertex-ai/generative-ai/docs/music/music-gen-prompt-guide) 

    Here is an example: "Dark Hybrid Film Score, Los Angeles, Studio recording, ominous and relentless. Pristine contemporary Instrumental, recorded live London, Dark Trailer Music. A blend of driving percussive synths, distorted orchestral elements, and filmic pulse textures, with instruments such as synths, distorted strings, brass, and hybrid percussion, and a cinematic approach, featuring pulsing rhythms, dissonant harmonies, and a sense of impending dread, evoking a tense and foreboding atmosphere"

    Your process:
    1. Use the `analyze_video_frames_from_supabase` tool with the video ID to analyze frames
    2. Based on the visual content, generate a detailed music prompt following the Lyria format

    Focus on:
    - Visual mood and atmosphere
    - Movement and energy in the scene
    - Color palette and lighting
    - Emotional tone
    - Suitable music style and instruments

    Generate ONLY the music prompt, no additional text or explanations.
    """,
    tools=[get_frames_from_supabase, analyze_video_frames_from_supabase],
    output_key="music_prompt",  # This stores the music prompt in session state
)
