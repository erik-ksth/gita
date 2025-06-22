from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
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


@app.get("/", response_model=dict)
def root():
    return {
        "message": "Gita API is running!",
        "endpoints": ["/health", "/generate-music-from-video"],
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
