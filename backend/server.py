from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import shutil
import tempfile
from typing import Optional, List
from agents import run_video_to_music_workflow
from agents.video_processing_agent import extract_frames, get_video_info
from supabase_config import supabase, STORAGE_BUCKETS

app = FastAPI(title="Gita API", description="AI Music Generation API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Ensure uploads directory exists (for temporary files)
os.makedirs("uploads", exist_ok=True)

# Pydantic models for request/response
class GenerateMusicRequest(BaseModel):
    video_path: str  # In a real app, this would be a file upload
    vision_prompt: str
    music_prompt: str


class GenerateMusicResponse(BaseModel):
    final_video_path: str


class HealthResponse(BaseModel):
    status: str
    message: str


class VideoUploadResponse(BaseModel):
    message: str
    video_id: str
    filename: str
    file_url: str
    video_info: dict
    extracted_frames: List[str]


def upload_video_to_supabase(file_data: bytes, filename: str) -> str:
    """Upload video to Supabase storage and return public URL."""
    try:
        result = supabase.storage.from_(STORAGE_BUCKETS["videos"]).upload(
            filename, file_data, {"content-type": "video/mp4"}
        )
        
        if result:
            public_url = supabase.storage.from_(STORAGE_BUCKETS["videos"]).get_public_url(filename)
            print(f"Video uploaded to Supabase: {filename}")
            return public_url
        else:
            raise Exception("Failed to upload video to Supabase")
            
    except Exception as e:
        print(f"Error uploading video to Supabase: {e}")
        raise


def save_video_to_database(filename: str, original_filename: str, file_url: str, 
                          video_info: dict, trim_info: dict) -> str:
    """Save video metadata to Supabase database and return video ID."""
    try:
        result = supabase.table("videos").insert({
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
            "processing_status": "uploaded"
        }).execute()
        
        if result.data:
            video_id = result.data[0]["id"]
            print(f"Video metadata saved to database: {filename} (ID: {video_id})")
            return video_id
        else:
            raise Exception("Failed to save video to database")
            
    except Exception as e:
        print(f"Error saving video to database: {e}")
        raise


def update_video_frames_status(video_id: str, frames_extracted: bool = True) -> None:
    """Update video processing status in database."""
    try:
        supabase.table("videos").update({
            "frames_extracted": frames_extracted,
            "processing_status": "completed" if frames_extracted else "processing"
        }).eq("id", video_id).execute()
        
        print(f"Updated video {video_id} frames status: {frames_extracted}")
        
    except Exception as e:
        print(f"Error updating video status: {e}")


@app.get("/", response_model=dict)
def root():
    return {
        "message": "Gita API is running!",
        "endpoints": ["/health", "/generate-music-from-video", "/upload-video"],
        "docs": "/docs",
    }


@app.post("/generate-music-from-video", response_model=GenerateMusicResponse)
def generate_music_from_video(request: GenerateMusicRequest):
    try:
        final_video_path = run_video_to_music_workflow(
            video_path=request.video_path,
            vision_prompt=request.vision_prompt,
            music_prompt=request.music_prompt,
        )
        return GenerateMusicResponse(final_video_path=final_video_path)

    except Exception as e:
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
    duration: Optional[float] = Form(None)
):
    try:
        # Validate file type
        if not video.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Generate unique filename
        import uuid
        file_extension = os.path.splitext(video.filename or "video.mp4")[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Read video data
        video_data = await video.read()
        
        print(f"Processing video upload: {unique_filename}")
        
        # Save to temporary file for processing
        temp_path = os.path.join("uploads", unique_filename)
        with open(temp_path, "wb") as buffer:
            buffer.write(video_data)
        
        # Get video information
        video_info = get_video_info(temp_path)
        print(f"Video info: {video_info}")
        
        # Upload video to Supabase
        print("Uploading video to Supabase...")
        file_url = upload_video_to_supabase(video_data, unique_filename)
        
        # Prepare trim info
        trim_info = {
            "originalFileName": originalFileName,
            "trimStart": trimStart,
            "trimEnd": trimEnd,
            "duration": duration
        }
        
        # Save video metadata to database
        print("Saving video metadata to database...")
        video_id = save_video_to_database(
            filename=unique_filename,
            original_filename=originalFileName or video.filename,
            file_url=file_url,
            video_info=video_info,
            trim_info=trim_info
        )
        
        # Extract frames and upload to Supabase
        print("Starting automatic frame extraction...")
        extracted_frames = extract_frames(temp_path, num_frames=5, video_id=video_id)
        print(f"Extracted {len(extracted_frames)} frames automatically")
        
        # Update video status
        update_video_frames_status(video_id, frames_extracted=True)
        
        # Clean up temporary file
        os.remove(temp_path)
        print(f"Cleaned up temporary file: {temp_path}")
        
        return VideoUploadResponse(
            message=f"Video uploaded successfully and {len(extracted_frames)} frames extracted",
            video_id=video_id,
            filename=unique_filename,
            file_url=file_url,
            video_info=video_info,
            extracted_frames=extracted_frames
        )
        
    except Exception as e:
        # Clean up temp file on error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        
        print(f"Error during upload/processing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload/process video: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
