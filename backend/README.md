# Gita Backend - Supabase-Powered API

This is the backend API for Gita, an AI-powered music generation app that creates music from video content. The backend uses Supabase for storage and database operations.

## Features

- ✅ **Video Upload to Supabase**: Videos are stored in Supabase storage instead of local filesystem
- ✅ **Automatic Frame Extraction**: Extracts 5 frames from uploaded videos and stores them in Supabase
- ✅ **Database Integration**: All metadata stored in Supabase PostgreSQL database
- ✅ **AI Music Generation**: Uses AI agents to analyze video content and generate appropriate music
- ✅ **Video Processing**: Combines original video with generated music

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `POST /upload-video` - Upload video to Supabase storage
- `GET /list-videos` - List all uploaded videos with metadata
- `POST /generate-music-from-video` - Generate music for a specific video ID

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
```

**Response:**

```json
{
  "message": "Video uploaded to Supabase successfully and 5 frames extracted",
  "filename": "unique-filename.mp4",
  "file_path": "https://supabase-storage-url/videos/unique-filename.mp4",
  "video_id": "uuid-of-video",
  "trim_info": { ... },
  "video_info": { ... },
  "extracted_frames": [ ... ]
}
```

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
      "processing_status": "processed",
      "frames_extracted": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## Database Schema

The app uses the following Supabase tables:

- **videos**: Stores video metadata and processing status
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
3. **Database**: All metadata is stored in Supabase PostgreSQL
4. **Workflow**: Video processing uses video IDs instead of file paths
5. **Cleanup**: Temporary files are automatically cleaned up after processing

## Architecture

```
Frontend (React)
    ↓ (uploads video)
Backend (FastAPI)
    ↓ (stores video & metadata)
Supabase (Storage + Database)
    ↓ (processes video)
AI Agents (Vision + Music Generation)
    ↓ (creates final video)
Supabase (Storage)
```

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
