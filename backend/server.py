from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import shutil
from typing import Optional
from agents import run_video_to_music_workflow

app = FastAPI(title="Gita API", description="AI Music Generation API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Ensure uploads directory exists
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
    filename: str
    file_path: str
    trim_info: dict


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
        
        # Generate a unique filename
        import uuid
        file_extension = os.path.splitext(video.filename or "video.mp4")[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join("uploads", unique_filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        # Prepare trim info
        trim_info = {
            "originalFileName": originalFileName,
            "trimStart": trimStart,
            "trimEnd": trimEnd,
            "duration": duration
        }
        
        return VideoUploadResponse(
            message="Video uploaded successfully",
            filename=unique_filename,
            file_path=file_path,
            trim_info=trim_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
