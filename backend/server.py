from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Gita API", description="Music search API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str


class MusicTrack(BaseModel):
    title: str
    artist: str
    genre: str
    duration: str
    mood: str
    download_url: str


class SearchResponse(BaseModel):
    results: List[MusicTrack]


class HealthResponse(BaseModel):
    status: str
    message: str


# Mock music database - in a real app, this would come from a database
MOCK_MUSIC_DB = [
    {
        "title": "Upbeat Adventure",
        "artist": "Creative Commons",
        "genre": "Electronic",
        "duration": "2:45",
        "mood": "energetic",
        "download_url": "https://example.com/upbeat-adventure.mp3",
    },
    {
        "title": "Calm Waters",
        "artist": "Free Music Archive",
        "genre": "Ambient",
        "duration": "3:20",
        "mood": "relaxing",
        "download_url": "https://example.com/calm-waters.mp3",
    },
    {
        "title": "Tech Startup",
        "artist": "CC Mixter",
        "genre": "Corporate",
        "duration": "1:55",
        "mood": "professional",
        "download_url": "https://example.com/tech-startup.mp3",
    },
    {
        "title": "Summer Vibes",
        "artist": "Incompetech",
        "genre": "Pop",
        "duration": "2:30",
        "mood": "happy",
        "download_url": "https://example.com/summer-vibes.mp3",
    },
    {
        "title": "Night Drive",
        "artist": "Free Music Archive",
        "genre": "Synthwave",
        "duration": "4:15",
        "mood": "mysterious",
        "download_url": "https://example.com/night-drive.mp3",
    },
]


@app.get("/", response_model=dict)
def root():
    return {
        "message": "Gita API is running!",
        "endpoints": ["/health", "/search-music"],
        "docs": "/docs",
    }


@app.post("/search-music", response_model=SearchResponse)
def search_music(request: SearchRequest):
    try:
        query = request.query.lower()

        if not query:
            return SearchResponse(results=[])

        # Simple search logic - in a real app, you'd use a proper search engine
        results = []
        for track_data in MOCK_MUSIC_DB:
            track = MusicTrack(**track_data)
            if (
                query in track.title.lower()
                or query in track.artist.lower()
                or query in track.genre.lower()
                or query in track.mood.lower()
            ):
                results.append(track)

        # If no exact matches, return all tracks (for demo purposes)
        if not results:
            results = [MusicTrack(**track_data) for track_data in MOCK_MUSIC_DB[:3]]

        return SearchResponse(results=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy", message="Gita API is running!")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
