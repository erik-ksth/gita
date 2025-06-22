import os
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

    # Step 1: Check if frames already exist, if not extract them
    frames_dir = os.path.join(os.path.dirname(video_path), "frames")
    
    if os.path.exists(frames_dir) and os.listdir(frames_dir):
        # Use existing frames
        existing_frames = [
            os.path.join(frames_dir, f) 
            for f in sorted(os.listdir(frames_dir)) 
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        print(f"Using existing {len(existing_frames)} frames from upload")
        frames = existing_frames
    else:
        # Extract frames if they don't exist
        print("No existing frames found, extracting frames...")
        frames = extract_frames(video_path=video_path, num_frames=5)
        print(f"Frames extracted: {len(frames)}")

    # Step 2: Analyze frames using the vision analysis agent
    description = analyze_images_from_supabase(image_paths=frames)
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
from .vision_analysis_agent import analyze_images_from_supabase
from .music_generation_agent import generate_music 