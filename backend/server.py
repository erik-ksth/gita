from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import uuid
from typing import Optional, List
from agents import run_video_to_music_workflow
from agents.video_processor_agent import (
    extract_frames,
    get_video_info,
    combine_video_with_audio_from_supabase,
)
from agents.prompt_generator_agent import analyze_video_frames_from_supabase
from agents.prompt_checker_agent import validate_and_fix_prompt
from agents.music_generator_agent import generate_music_from_video_id
from supabase_config import supabase, STORAGE_BUCKETS

app = FastAPI(title="Gita API", description="AI Music Generation API")

# Set up CORS using an environment variable
# For local dev, default to allowing http://localhost:3000 (standard React port)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000")
origins = [origin.strip() for origin in CORS_ORIGINS.split(",")]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create temporary uploads directory for video processing (files are cleaned up after processing)
os.makedirs("uploads", exist_ok=True)


# Pydantic models for request/response
class GenerateMusicRequest(BaseModel):
    video_id: str  # UUID of the video stored in Supabase
    vision_prompt: str
    music_prompt: str


class GenerateMusicResponse(BaseModel):
    final_video_path: str


class HealthResponse(BaseModel):
    status: str
    message: str


class VideoUploadResponse(BaseModel):
    message: str
    filename: str
    file_path: str
    video_id: str
    trim_info: dict
    video_info: dict
    extracted_frames: List[str]
    music_generated: bool
    music_url: Optional[str] = None
    final_video_created: bool
    final_video_url: Optional[str] = None


class VideoListResponse(BaseModel):
    videos: List[dict]


class MusicGenerationListResponse(BaseModel):
    music_generations: List[dict]


def upload_video_to_supabase(video_data: bytes, filename: str) -> str:
    """
    Upload video to Supabase storage.

    Args:
        video_data: The video file data as bytes
        filename: The filename for the video

    Returns:
        The public URL of the uploaded video
    """
    try:
        # Upload video to Supabase storage
        result = supabase.storage.from_(STORAGE_BUCKETS["videos"]).upload(
            filename, video_data, {"content-type": "video/mp4"}
        )

        if result:
            # Get public URL
            public_url = supabase.storage.from_(
                STORAGE_BUCKETS["videos"]
            ).get_public_url(filename)
            print(f"Video uploaded to Supabase: {filename}")
            return public_url
        else:
            raise Exception("Failed to upload video to Supabase")

    except Exception as e:
        print(f"Error uploading video to Supabase: {e}")
        raise


def save_video_to_database(
    filename: str,
    original_filename: str,
    file_url: str,
    video_info: dict,
    trim_info: dict,
) -> str:
    """
    Save video metadata to Supabase database.

    Args:
        filename: The video filename
        original_filename: The original filename before processing
        file_url: The Supabase storage URL
        video_info: Dictionary containing video metadata
        trim_info: Dictionary containing trim information

    Returns:
        The video UUID
    """
    try:
        result = (
            supabase.table("videos")
            .insert(
                {
                    "filename": filename,
                    "original_filename": original_filename,
                    "file_path": file_url,
                    "file_size_mb": video_info.get("file_size_mb"),
                    "duration_seconds": video_info.get("duration_seconds"),
                    "fps": video_info.get("fps"),
                    "resolution": video_info.get("resolution"),
                    "frame_count": video_info.get("frame_count"),
                    "trim_start": trim_info.get("trimStart"),
                    "trim_end": trim_info.get("trimEnd"),
                    "trim_duration": trim_info.get("duration"),
                    "processing_status": "uploaded",
                    "frames_extracted": False,
                }
            )
            .execute()
        )

        if result.data:
            video_id = result.data[0]["id"]
            print(f"Video metadata saved to database: {filename} (ID: {video_id})")
            return video_id
        else:
            raise Exception("Failed to save video to database")

    except Exception as e:
        print(f"Error saving video to database: {e}")
        raise


def update_video_frames_extracted(video_id: str):
    """
    Update the video record to indicate frames have been extracted.

    Args:
        video_id: The UUID of the video
    """
    try:
        result = (
            supabase.table("videos")
            .update({"frames_extracted": True, "processing_status": "processed"})
            .eq("id", video_id)
            .execute()
        )

        if result.data:
            print(f"Updated video {video_id} - frames extracted")
        else:
            print(f"Warning: Could not update video {video_id}")

    except Exception as e:
        print(f"Error updating video frames status: {e}")


def save_vision_analysis_to_database(video_id: str, analysis_result: str) -> str:
    """
    Save vision analysis result to Supabase database.

    Args:
        video_id: The UUID of the video
        analysis_result: The generated music prompt from vision analysis

    Returns:
        Success message
    """
    try:
        result = (
            supabase.table("videos")
            .update(
                {
                    "vision_analysis": analysis_result,
                    "processing_status": "analyzed",  # Will be updated to "music_generating" if music generation starts
                }
            )
            .eq("id", video_id)
            .execute()
        )

        if result.data:
            print(f"Vision analysis saved for video {video_id}")
            return "Vision analysis saved successfully"
        else:
            print(f"Warning: Could not update video {video_id} with vision analysis")
            return "Warning: Could not save vision analysis"

    except Exception as e:
        print(f"Error saving vision analysis to database: {e}")
        raise


def update_video_status(video_id: str, status: str) -> None:
    """
    Update video processing status.

    Args:
        video_id: The UUID of the video
        status: The new processing status
    """
    try:
        result = (
            supabase.table("videos")
            .update({"processing_status": status})
            .eq("id", video_id)
            .execute()
        )

        if result.data:
            print(f"Updated video {video_id} status to: {status}")
        else:
            print(f"Warning: Could not update video {video_id} status")

    except Exception as e:
        print(f"Error updating video status: {e}")


@app.get("/", response_model=dict)
def root():
    return {
        "message": "Gita API is running!",
        "endpoints": [
            "/health",
            "/upload-video",
            "/list-videos",
            "/list-music-generations/{video_id}",
            "/generate-music-from-video",
        ],
        "docs": "/docs",
    }


@app.post("/generate-music-from-video", response_model=GenerateMusicResponse)
def generate_music_from_video(request: GenerateMusicRequest):
    try:
        # Validate that the video exists in the database
        result = (
            supabase.table("videos")
            .select("id, filename")
            .eq("id", request.video_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=404, detail=f"Video with ID {request.video_id} not found"
            )

        video_info = result.data[0]
        print(f"Processing video: {video_info['filename']} (ID: {request.video_id})")

        final_video_path = run_video_to_music_workflow(
            video_id=request.video_id,
            vision_prompt=request.vision_prompt,
            music_prompt=request.music_prompt,
        )
        return GenerateMusicResponse(final_video_path=final_video_path)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Error in generate_music_from_video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy", message="Gita API is running!")


@app.post("/upload-video", response_model=VideoUploadResponse)
async def upload_video(
    video: UploadFile = File(...),
    originalFileName: Optional[str] = Form(None),
    trimStart: Optional[float] = Form(None),
    trimEnd: Optional[float] = Form(None),
    duration: Optional[float] = Form(None),
    visionPrompt: Optional[str] = Form(None),
):
    temp_file_path = None

    try:
        # Validate file type
        if not video.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="File must be a video")

        # Generate a unique filename
        file_extension = os.path.splitext(video.filename or "video.mp4")[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Read video data
        video_data = await video.read()

        # Create temporary file for processing
        temp_file_path = os.path.join("uploads", unique_filename)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(video_data)

        print(f"Video temporarily saved for processing: {temp_file_path}")

        # Get video information
        video_info = get_video_info(temp_file_path)
        print(f"Video info: {video_info}")

        # Upload video to Supabase
        video_url = upload_video_to_supabase(video_data, unique_filename)
        print(f"Video uploaded to Supabase: {video_url}")

        # Prepare trim info
        trim_info = {
            "originalFileName": originalFileName,
            "trimStart": trimStart,
            "trimEnd": trimEnd,
            "duration": duration,
        }

        # Save video metadata to database
        video_id = save_video_to_database(
            filename=unique_filename,
            original_filename=originalFileName or video.filename,
            file_url=video_url,
            video_info=video_info,
            trim_info=trim_info,
        )

        # Automatically extract frames (exactly 5 frames with equal intervals)
        print("Starting automatic frame extraction...")
        extracted_frames = extract_frames(
            temp_file_path, num_frames=5, video_id=video_id
        )
        print(f"Extracted {len(extracted_frames)} frames automatically")

        # Update video record to indicate frames have been extracted
        update_video_frames_extracted(video_id)

        # Automatically analyze the extracted frames
        print("Starting automatic vision analysis with Groq...")
        vision_analysis_completed = False
        try:
            vision_analysis_result = analyze_video_frames_from_supabase(
                video_id, visionPrompt
            )
            print(f"Vision analysis completed: {vision_analysis_result[:100]}...")

            # Validate and improve the generated prompt
            print("Validating and improving the generated prompt...")
            validated_analysis = validate_and_fix_prompt(vision_analysis_result)

            if validated_analysis != vision_analysis_result:
                print(
                    f"Prompt was improved: {vision_analysis_result[:50]}... → {validated_analysis[:50]}..."
                )
                vision_analysis_result = validated_analysis

            # Save the analysis result to the database
            save_vision_analysis_to_database(video_id, vision_analysis_result)
            print("Vision analysis saved to database")
            vision_analysis_completed = True

        except Exception as analysis_error:
            print(f"Warning: Vision analysis failed: {analysis_error}")
            # Continue with upload even if analysis fails

        # Automatically generate music after successful vision analysis
        music_generation_completed = False
        music_url = None
        if vision_analysis_completed:
            print("Starting automatic music generation...")
            update_video_status(video_id, "music_generating")

            try:
                music_url = generate_music_from_video_id(
                    video_id, custom_music_prompt=None
                )
                print(f"Music generation completed: {music_url}")
                music_generation_completed = True
                update_video_status(video_id, "music_completed")

            except Exception as music_error:
                print(f"Warning: Music generation failed: {music_error}")
                update_video_status(video_id, "music_failed")
                # Continue with upload even if music generation fails

        # Automatically combine video with music after successful music generation
        final_video_completed = False
        final_video_url = None
        if music_generation_completed and music_url:
            print("Starting automatic video combination with generated music...")
            update_video_status(video_id, "combining_video")

            try:
                # Extract filename from music URL
                music_filename = music_url.split("/")[-1] if music_url else None

                # Combine video with generated music
                final_video_info = combine_video_with_audio_from_supabase(
                    video_id=video_id, audio_filename=music_filename
                )

                final_video_url = final_video_info["final_video_url"]
                print(f"Video combination completed: {final_video_url}")
                final_video_completed = True
                update_video_status(video_id, "completed")

                # Update the music generation record with the final video path
                try:
                    from agents.music_generator_agent import (
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

            except Exception as combination_error:
                print(f"Warning: Video combination failed: {combination_error}")
                update_video_status(video_id, "combination_failed")
                # Continue with upload even if video combination fails

        # Create response message based on what was completed
        message_parts = [
            f"Video uploaded to Supabase successfully, {len(extracted_frames)} frames extracted"
        ]
        if vision_analysis_completed:
            message_parts.append("vision analysis completed")
        if music_generation_completed:
            message_parts.append("music generated automatically")
        if final_video_completed:
            message_parts.append("final video with music created")

        response_message = ", ".join(message_parts)

        return VideoUploadResponse(
            message=response_message,
            filename=unique_filename,
            file_path=video_url,  # Return Supabase URL instead of local path
            video_id=video_id,
            trim_info=trim_info,
            video_info=video_info,
            extracted_frames=extracted_frames,
            music_generated=music_generation_completed,
            music_url=music_url,
            final_video_created=final_video_completed,
            final_video_url=final_video_url,
        )

    except Exception as e:
        print(f"Error during upload/processing: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to upload/process video: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as cleanup_error:
                print(
                    f"Warning: Could not clean up temporary file {temp_file_path}: {cleanup_error}"
                )


@app.get("/list-videos", response_model=VideoListResponse)
def list_videos():
    """
    Get a list of all uploaded videos with their metadata.
    """
    try:
        result = (
            supabase.table("videos")
            .select(
                "id, filename, original_filename, duration_seconds, resolution, "
                "processing_status, frames_extracted, vision_analysis, created_at"
            )
            .order("created_at", desc=True)
            .execute()
        )

        videos = []
        if result.data:
            for video in result.data:
                videos.append(
                    {
                        "id": video["id"],
                        "filename": video["filename"],
                        "original_filename": video["original_filename"],
                        "duration_seconds": video["duration_seconds"],
                        "resolution": video["resolution"],
                        "processing_status": video["processing_status"],
                        "frames_extracted": video["frames_extracted"],
                        "vision_analysis_completed": bool(video.get("vision_analysis")),
                        "created_at": video["created_at"],
                    }
                )

        return VideoListResponse(videos=videos)

    except Exception as e:
        print(f"Error listing videos: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list videos: {str(e)}")


@app.get(
    "/list-music-generations/{video_id}", response_model=MusicGenerationListResponse
)
def list_music_generations(video_id: str):
    """
    Get all music generation records for a specific video.
    """
    try:
        result = (
            supabase.table("music_generations")
            .select("*")
            .eq("video_id", video_id)
            .order("created_at", desc=True)
            .execute()
        )

        music_generations = []
        if result.data:
            for generation in result.data:
                music_generations.append(
                    {
                        "id": generation["id"],
                        "video_id": generation["video_id"],
                        "vision_prompt": generation.get("vision_prompt"),
                        "music_prompt": generation.get("music_prompt"),
                        "music_file_path": generation.get("music_file_path"),
                        "music_file_size_mb": generation.get("music_file_size_mb"),
                        "final_video_path": generation.get("final_video_path"),
                        "generation_status": generation.get("generation_status"),
                        "created_at": generation["created_at"],
                        "updated_at": generation.get("updated_at"),
                    }
                )

        return MusicGenerationListResponse(music_generations=music_generations)

    except Exception as e:
        print(f"Error listing music generations for video {video_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list music generations: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
