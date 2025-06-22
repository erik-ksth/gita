import os
from .video_processing_agent import video_processing_agent, download_video_from_supabase, combine_video_with_audio_from_supabase
from .vision_analysis_agent import vision_analysis_agent, analyze_video_frames_from_supabase
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

    # Step 1: Get the pre-computed vision analysis from the database
    try:
        result = supabase.table("videos").select("vision_analysis, processing_status").eq("id", video_id).execute()
        
        if not result.data:
            raise Exception(f"Video with ID {video_id} not found in database")
        
        video_data = result.data[0]
        stored_analysis = video_data.get("vision_analysis")
        processing_status = video_data.get("processing_status")
        
        if stored_analysis:
            # Use the pre-computed analysis result
            print(f"Using pre-computed vision analysis from database")
            description = stored_analysis
        else:
            # Fallback: Analyze frames using video_id if no stored analysis exists
            print("No pre-computed analysis found, analyzing frames now...")
            description = analyze_video_frames_from_supabase(video_id)
            
            # Save the analysis result for future use
            try:
                supabase.table("videos").update({
                    "vision_analysis": description,
                    "processing_status": "analyzed"
                }).eq("id", video_id).execute()
                print("Saved vision analysis to database for future use")
            except Exception as save_error:
                print(f"Warning: Could not save analysis result: {save_error}")
            
    except Exception as e:
        print(f"Error retrieving video data: {e}")
        raise

    print(f"Scene description: {description}")

    # Step 2: Generate music using the music generation agent
    music_file = generate_music(description=description, custom_prompt=music_prompt)
    print(f"Music file generated: {music_file}")

    # Step 3: Combine video with audio using Supabase workflow
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
from .vision_analysis_agent import analyze_video_frames_from_supabase
from .music_generation_agent import generate_music 