import os
from .video_processor_agent import (
    video_processor_agent,
    download_video_from_supabase,
    combine_video_with_audio_from_supabase,
)
from .prompt_generator_agent import (
    prompt_generator_agent,
    analyze_video_frames_from_supabase,
)
from .prompt_checker_agent import (
    prompt_checker_agent,
    validate_and_fix_prompt,
)
from .music_generator_agent import music_generator_agent, generate_music_from_video_id
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

    # Step 1: Verify video exists and check analysis status
    try:
        result = (
            supabase.table("videos")
            .select("vision_analysis, processing_status, filename")
            .eq("id", video_id)
            .execute()
        )

        if not result.data:
            raise Exception(f"Video with ID {video_id} not found in database")

        video_data = result.data[0]
        stored_analysis = video_data.get("vision_analysis")
        processing_status = video_data.get("processing_status")
        filename = video_data.get("filename", "unknown")

        print(f"Video found: {filename} (Status: {processing_status})")

        if not stored_analysis:
            # If no analysis exists, run it now
            print("No pre-computed analysis found, analyzing frames now...")
            stored_analysis = analyze_video_frames_from_supabase(
                video_id, vision_prompt
            )

            # Validate and improve the generated prompt
            print("Validating and improving the generated prompt...")
            validated_analysis = validate_and_fix_prompt(stored_analysis)

            if validated_analysis != stored_analysis:
                print(
                    f"Prompt was improved: {stored_analysis[:50]}... → {validated_analysis[:50]}..."
                )
                stored_analysis = validated_analysis

            # Save the analysis result for future use
            try:
                supabase.table("videos").update(
                    {
                        "vision_analysis": stored_analysis,
                        "processing_status": "analyzed",
                    }
                ).eq("id", video_id).execute()
                print("Saved vision analysis to database for future use")
            except Exception as save_error:
                print(f"Warning: Could not save analysis result: {save_error}")
        else:
            print(f"Using pre-computed vision analysis from database")

            # Still validate the stored analysis to ensure quality
            print("Validating stored vision analysis...")
            validated_analysis = validate_and_fix_prompt(stored_analysis)
            if validated_analysis != stored_analysis:
                print(
                    f"Stored prompt was improved: {stored_analysis[:50]}... → {validated_analysis[:50]}..."
                )
                stored_analysis = validated_analysis

                # Update the improved analysis in the database
                try:
                    supabase.table("videos").update(
                        {
                            "vision_analysis": stored_analysis,
                        }
                    ).eq("id", video_id).execute()
                    print("Updated improved vision analysis in database")
                except Exception as update_error:
                    print(
                        f"Warning: Could not update improved analysis: {update_error}"
                    )

    except Exception as e:
        print(f"Error retrieving video data: {e}")
        raise

    print(f"Vision analysis available for music generation")

    # Step 2: Generate music using the video_id-based approach
    try:
        print("Generating music using vision analysis...")
        music_url = generate_music_from_video_id(
            video_id=video_id,
            custom_music_prompt=music_prompt if music_prompt else None,
        )
        print(f"Music generated and uploaded to Supabase: {music_url}")

    except Exception as e:
        print(f"Error generating music: {e}")
        raise

    # Step 3: Combine video with audio using Supabase workflow
    try:
        # Extract filename from the music URL for the audio parameter
        music_filename = music_url.split("/")[-1] if music_url else None

        # Use the existing Supabase function to combine video and audio
        final_video_info = combine_video_with_audio_from_supabase(
            video_id=video_id, audio_filename=music_filename
        )

        final_video_url = final_video_info["final_video_url"]
        print(f"Final video created and uploaded to Supabase: {final_video_url}")

        # Update the latest music generation record with the final video path
        try:
            from .music_generator_agent import (
                get_music_generations_for_video,
                update_music_generation_record,
            )

            # Get the most recent music generation for this video
            music_generations = get_music_generations_for_video(video_id)
            if music_generations:
                latest_generation = music_generations[0]  # Most recent first
                update_music_generation_record(
                    latest_generation["id"], final_video_path=final_video_url
                )
                print(f"Updated music generation record with final video path")
        except Exception as update_error:
            print(
                f"Warning: Could not update music generation record with final video: {update_error}"
            )

        # Update video status to completed
        try:
            supabase.table("videos").update({"processing_status": "completed"}).eq(
                "id", video_id
            ).execute()
            print("Updated video status to completed")
        except Exception as status_error:
            print(f"Warning: Could not update video status: {status_error}")

        return final_video_url

    except Exception as e:
        print(f"Error combining video with audio: {e}")
        raise


def run_video_to_music_workflow_legacy(
    video_path: str, vision_prompt: str, music_prompt: str
):
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
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
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

    # Step 3: Generate music using the legacy music generation
    music_file = generate_music(description=description, custom_prompt=music_prompt)
    print(f"Music file generated: {music_file}")

    # Step 4: Attach audio to video
    final_video = attach_audio(video_path=video_path, audio_path=music_file)
    print(f"Final video created: {final_video}")

    return final_video


# Import the functions from the agents
from .video_processor_agent import extract_frames, attach_audio
from .prompt_generator_agent import analyze_video_frames_from_supabase
from .music_generator_agent import (
    generate_music,
)  # Keep legacy function for backward compatibility
