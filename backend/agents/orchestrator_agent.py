import os
from .video_processing_agent import video_processing_agent, download_video_from_supabase, combine_video_with_audio_from_supabase
from .vision_analysis_agent import vision_analysis_agent
from .music_generation_agent import music_generation_agent
from supabase_config import supabase

def run_video_to_music_workflow(video_id: str, vision_prompt: str, music_prompt: str):
    """
    Executes the entire video-to-music workflow using Supabase-stored videos.

    Args:
        video_id: UUID of the video stored in Supabase.
        vision_prompt: Custom prompt for the vision analysis.
        music_prompt: Custom prompt for the music generation.
    """
    print(f"Starting workflow for video ID: {video_id}")

    # Step 1: Get extracted frames from Supabase database
    try:
        result = supabase.table("frames").select("file_path").eq("video_id", video_id).execute()
        
        if result.data and len(result.data) > 0:
            # Use existing frames from Supabase
            frames = [frame["file_path"] for frame in result.data]
            print(f"Using existing {len(frames)} frames from Supabase")
        else:
            # This should not happen as frames are extracted during upload
            # But we can fallback to re-extracting if needed
            print("No frames found in database. This should not happen after upload.")
            raise Exception("No frames found for this video. Please re-upload the video.")
            
    except Exception as e:
        print(f"Error retrieving frames from database: {e}")
        raise

    # Step 2: Analyze frames using the vision analysis agent
    description = analyze_images_from_supabase(image_paths=frames)
    print(f"Scene description: {description}")

    # Step 3: Generate music using the music generation agent
    music_file = generate_music(description=description, custom_prompt=music_prompt)
    print(f"Music file generated: {music_file}")

    # Step 4: Combine video with audio using Supabase workflow
    try:
        # Extract just the filename from the music file path for the audio parameter
        audio_filename = os.path.basename(music_file) if music_file else None
        
        # Use the existing Supabase function to combine video and audio
        final_video_info = combine_video_with_audio_from_supabase(
            video_id=video_id, 
            audio_filename=audio_filename
        )
        
        print(f"Final video created and uploaded to Supabase: {final_video_info['final_video_url']}")
        return final_video_info["final_video_url"]
        
    except Exception as e:
        print(f"Error combining video with audio: {e}")
        raise

def run_video_to_music_workflow_legacy(video_path: str, vision_prompt: str, music_prompt: str):
    """
    Legacy workflow function for local file paths (kept for backward compatibility).
    """
    print("Starting legacy workflow...")

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