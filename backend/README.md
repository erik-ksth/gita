# Gita Backend - Supabase-Powered API

This is the backend API for Gita, an AI-powered music generation app that creates music from video content. The backend uses Supabase for storage and database operations.

## Features

- ✅ **Video Upload to Supabase**: Videos are stored in Supabase storage instead of local filesystem
- ✅ **Automatic Frame Extraction**: Extracts 5 frames from uploaded videos and stores them in Supabase
- ✅ **Groq Vision Analysis**: Analyzes extracted frames using Groq's vision model with custom prompts
- ✅ **Database Integration**: All metadata stored in Supabase PostgreSQL database
- ✅ **AI Music Generation**: Uses AI agents to analyze video content and generate appropriate music
- ✅ **Video Processing**: Combines original video with generated music
- ✅ **Optimized Workflow**: Pre-computed analysis makes music generation faster

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `POST /upload-video` - Upload video to Supabase storage (includes automatic frame extraction and Groq vision analysis)
- `GET /list-videos` - List all uploaded videos with metadata
- `POST /generate-music-from-video` - Generate music for a specific video ID (uses pre-computed analysis)

### Upload Video

```bash
POST /upload-video
Content-Type: multipart/form-data

Fields:
- video: Video file (required)
- originalFileName: Original filename (optional)
- trimStart: Trim start time in seconds (optional)
- trimEnd: Trim end time in seconds (optional)
- duration: Video duration (optional)
- visionPrompt: Custom prompt for Groq vision analysis (optional)
```

**Response:**

```json
{
  "message": "Video uploaded to Supabase successfully, 5 frames extracted, and vision analysis completed",
  "filename": "unique-filename.mp4",
  "file_path": "https://supabase-storage-url/videos/unique-filename.mp4",
  "video_id": "uuid-of-video",
  "trim_info": { ... },
  "video_info": { ... },
  "extracted_frames": [ ... ]
}
```

**What happens automatically:**

1. Video is uploaded to Supabase storage
2. 5 frames are extracted at equal intervals
3. Frames are uploaded to Supabase storage
4. **Groq vision analysis** is performed on the frames with optional custom prompt
5. Analysis result (music generation prompt) is stored in the database
6. Video status is updated to "analyzed"

### Generate Music from Video

```bash
POST /generate-music-from-video
Content-Type: application/json

{
  "video_id": "uuid-of-uploaded-video",
  "vision_prompt": "Custom vision analysis prompt",
  "music_prompt": "Custom music generation prompt"
}
```

**Response:**

```json
{
  "final_video_path": "https://supabase-storage-url/final-videos/final-video.mp4"
}
```

**What happens:**

1. Uses pre-computed vision analysis from database (faster!)
2. Generates music based on the analysis
3. Downloads original video from Supabase
4. Combines video with generated music
5. Uploads final video to Supabase
6. Returns final video URL

### List Videos

```bash
GET /list-videos
```

**Response:**

```json
{
  "videos": [
    {
      "id": "uuid",
      "filename": "video.mp4",
      "original_filename": "my-video.mp4",
      "duration_seconds": 30.5,
      "resolution": "1920x1080",
      "processing_status": "analyzed",
      "frames_extracted": true,
      "vision_analysis_completed": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## Processing Status Flow

The system tracks videos through these status stages:

1. **uploaded** - Video uploaded to Supabase
2. **processing** - Frames being extracted
3. **analyzed** - Vision analysis completed, ready for music generation
4. **completed** - Final video with music has been generated

## Database Schema

The app uses the following Supabase tables:

- **videos**: Stores video metadata, processing status, and vision analysis results
- **frames**: Stores extracted frame information and Supabase storage URLs
- **music_generations**: Stores music generation requests and results
- **final_videos**: Stores final combined video+music results

## Storage Buckets

The app uses these Supabase storage buckets:

- **videos**: Original uploaded videos
- **frames**: Extracted video frames (images)
- **music**: Generated music files
- **final-videos**: Final videos with music attached

## Environment Variables

Set these environment variables:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key
- `GROQ_API_KEY`: Your Groq API key for vision analysis
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins (default: "http://localhost:3000")

## Deployment

### Local Development

```bash
cd backend
pip install -r requirements.txt
python server.py
```

The server will run on `http://localhost:8000`

### Vercel Deployment

The app is configured for Vercel deployment:

1. Install Vercel CLI: `npm install -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel` (from the backend directory)
4. Set environment variables in Vercel dashboard
5. Redeploy: `vercel --prod`

## Key Changes from Local Storage

This version uses Supabase storage instead of local filesystem:

1. **Videos**: Uploaded directly to Supabase storage, not saved locally
2. **Frames**: Extracted frames are uploaded to Supabase storage
3. **Vision Analysis**: Automatically performed after upload and cached in database
4. **Database**: All metadata is stored in Supabase PostgreSQL
5. **Workflow**: Video processing uses video IDs instead of file paths
6. **Optimization**: Pre-computed analysis makes music generation much faster
7. **Cleanup**: Temporary files are automatically cleaned up after processing

## Architecture

```
Frontend (React)
    ↓ (uploads video)
Backend (FastAPI)
    ↓ (stores video & metadata)
Supabase (Storage + Database)
    ↓ (extracts frames automatically)
Frame Extraction Agent
    ↓ (analyzes frames using video_id)
Vision Analysis Agent
    ↓ (stores analysis in database)
Supabase Database
    ↓ (when user requests music generation)
Music Generation Agent
    ↓ (creates final video using video_id)
Video Processing Agent
    ↓ (uploads to storage)
Supabase (Storage)
```

## Agent Architecture

All agents now use a **video_id-based approach** for consistency and data isolation:

### 🎬 **Video Processing Agent**

- **Input**: `video_id`, video file path (for processing)
- **Functions**: `extract_frames()`, `combine_video_with_audio_from_supabase()`
- **Data Access**: Fetches video metadata from Supabase when needed
- **Output**: Stores frames and final videos in Supabase

### 👁️ **Vision Analysis Agent** (Groq Integration)

- **Input**: `video_id`, optional `custom_prompt`
- **Functions**: `analyze_video_frames_from_supabase()`, `send_images_to_groq()`
- **Data Access**: Downloads frame images from Supabase URLs, sends to Groq vision model
- **Groq Model**: `meta-llama/llama-4-scout-17b-16e-instruct`
- **Output**: Returns detailed music generation prompt from Groq analysis

### 🎵 **Music Generation Agent**

- **Input**: Generated music prompt from vision analysis
- **Functions**: `generate_music()`
- **Data Access**: Uses Google's Lyria model for music generation
- **Output**: Returns generated music file path

### 🎭 **Orchestrator Agent**

- **Input**: `video_id`, user prompts
- **Functions**: `run_video_to_music_workflow()`
- **Data Access**: Coordinates all agents using video_id
- **Output**: Final video URL with music

## Groq Vision Analysis

The system uses **Groq's vision model** to analyze video frames:

- **Model**: `meta-llama/llama-4-scout-17b-16e-instruct`
- **Input**: Up to 5 video frames + custom prompt
- **Process**: Downloads images from Supabase, encodes to base64, sends to Groq API
- **Output**: Detailed music generation prompt following Lyria format
- **Fallback**: Returns generic prompt if analysis fails
- **Storage**: Result stored in `vision_analysis` column in videos table

### Default Vision Prompt

If no custom prompt is provided, the system uses:

```
Analyze these video frames and generate a detailed, specific prompt for background music generation using Lyria. Follow the Lyria music generation prompt guide format.

Focus on:
- Visual mood and atmosphere
- Movement and energy in the scene
- Color palette and lighting
- Emotional tone
- Suitable music style and instruments

Generate ONLY the music prompt, no additional text or explanations.
```

## Key Benefits of Video ID Architecture

- 🔗 **Consistent Data Access**: All agents use video_id to fetch their required data
- 🔒 **Data Isolation**: Each agent manages its own Supabase queries
- 🚀 **Scalable**: Easy to add new agents that work with video_id
- 🛡️ **Robust**: Reduces data passing errors between agents
- 📊 **Traceable**: All operations linked to specific video records

## Testing

Test the API endpoints:

```bash
# Health check
curl https://your-api-url/health

# List videos
curl https://your-api-url/list-videos

# Upload video (use form data)
curl -X POST -F "video=@test-video.mp4" https://your-api-url/upload-video

# Generate music (use the video_id from upload response)
curl -X POST -H "Content-Type: application/json" \
  -d '{"video_id":"your-video-uuid","vision_prompt":"Analyze this video","music_prompt":"Create ambient music"}' \
  https://your-api-url/generate-music-from-video
```

## Troubleshooting

### Common Issues

1. **Supabase Connection**: Verify SUPABASE_URL and SUPABASE_ANON_KEY are set correctly
2. **Storage Buckets**: Ensure all required buckets exist in Supabase Storage
3. **File Upload**: Check file size limits in Supabase (default: 50MB)
4. **CORS**: Add your frontend domain to CORS_ORIGINS environment variable

### Database Setup

Make sure to run the SQL schema in `supabase_schema.sql` to create the required tables and buckets.

### Storage Setup

Create these buckets in your Supabase Storage dashboard:

- videos
- frames
- music
- final-videos

## API Documentation

Interactive API documentation is available at `/docs` when running the server.
