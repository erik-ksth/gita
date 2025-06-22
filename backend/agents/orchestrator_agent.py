from .video_processing_agent import video_processing_agent
from .vision_analysis_agent import vision_analysis_agent
from .music_generation_agent import music_generation_agent

def run_video_to_music_workflow(video_path: str, vision_prompt: str, music_prompt: str):
    """
    Executes the entire video-to-music workflow.

    Args:
        video_path: Path to the input video.
        vision_prompt: Custom prompt for the vision analysis.
        music_prompt: Custom prompt for the music generation.
    """
    print("Starting workflow...")

    # Step 1: Extract frames using the video processing agent
    frames = extract_frames(video_path=video_path)
    print(f"Frames extracted: {frames}")

    # Step 2: Analyze frames using the vision analysis agent
    description = analyze_images(image_paths=frames, prompt=vision_prompt)
    print(f"Scene description: {description}")

    # Step 3: Generate music using the music generation agent
    music_file = generate_music(description=description, custom_prompt=music_prompt)
    print(f"Music file generated: {music_file}")

    # Step 4: Attach audio to video
    final_video = attach_audio(video_path=video_path, audio_path=music_file)
    print(f"Final video created: {final_video}")

    return final_video

# Import the functions from the agents
from .video_processing_agent import extract_frames, attach_audio
from .vision_analysis_agent import analyze_images
from .music_generation_agent import generate_music 