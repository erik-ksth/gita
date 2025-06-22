import datetime
import os
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


def analyze_images_from_supabase(image_paths: List[str]) -> str:
    """Analyzes images from Supabase and generates a music prompt.

    Args:
        image_paths: A list of image paths stored in Supabase.

    Returns:
        A string containing the music generation prompt.
    """
    try:
        print(f"Analyzing {len(image_paths)} images from Supabase")

        # For now, we'll use a placeholder implementation
        # In a real implementation, you would:
        # 1. Download images from Supabase using the paths
        # 2. Process them with a vision model
        # 3. Generate a music prompt based on the visual content

        # Placeholder: Generate a music prompt based on the number of images
        if len(image_paths) > 0:
            # This is where you'd implement actual image analysis
            # For now, return a generic prompt
            music_prompt = "Ambient atmospheric music with gentle textures and flowing melodies, suitable for a contemplative scene with natural elements and soft lighting."
        else:
            music_prompt = "Neutral background music with subtle ambient tones."

        print(f"Generated music prompt: {music_prompt}")
        return music_prompt

    except Exception as e:
        print(f"Error analyzing images: {e}")
        return "Calm ambient music with peaceful undertones."


def get_images_from_supabase(video_id: str) -> List[str]:
    """Retrieves image paths from Supabase for a given video ID.

    Args:
        video_id: The ID of the video to get images for.

    Returns:
        A list of image paths stored in Supabase.
    """
    try:
        # Query Supabase for images associated with the video
        response = (
            supabase.table("video_frames")
            .select("image_path")
            .eq("video_id", video_id)
            .execute()
        )

        if response.data:
            image_paths = [item["image_path"] for item in response.data]
            print(f"Retrieved {len(image_paths)} image paths from Supabase")
            return image_paths
        else:
            print("No images found for the given video ID")
            return []

    except Exception as e:
        print(f"Error retrieving images from Supabase: {e}")
        return []


vision_analysis_agent = Agent(
    name="vision_analysis_agent",
    model=LiteLlm(model="groq/meta-llama/llama-4-maverick-17b-128e-instruct"),
    description="An agent that analyzes video frames from Supabase and generates music prompts using Groq.",
    instruction="""You are an expert LLM prompt engineer. Your TASK is to generate ONLY a detailed, specific prompt for background music generation using Lyria. When crafting the prompt, make sure to strictly adhere to the Lyria music generation prompt guide (https://cloud.google.com/vertex-ai/generative-ai/docs/music/music-gen-prompt-guide) 

Here is an example: "Dark Hybrid Film Score, Los Angeles, Studio recording, ominous and relentless. Pristine contemporary Instrumental, recorded live London, Dark Trailer Music. A blend of driving percussive synths, distorted orchestral elements, and filmic pulse textures, with instruments such as synths, distorted strings, brass, and hybrid percussion, and a cinematic approach, featuring pulsing rhythms, dissonant harmonies, and a sense of impending dread, evoking a tense and foreboding atmosphere"

Your process:
1. Retrieve image paths from Supabase using the `get_images_from_supabase` tool
2. Analyze the images using the `analyze_images_from_supabase` tool
3. Based on the visual content, generate a detailed music prompt following the Lyria format

Focus on:
- Visual mood and atmosphere
- Movement and energy in the scene
- Color palette and lighting
- Emotional tone
- Suitable music style and instruments

Generate ONLY the music prompt, no additional text or explanations.
""",
    tools=[get_images_from_supabase, analyze_images_from_supabase],
    output_key="music_prompt",  # This stores the music prompt in session state
)
