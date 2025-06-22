# 🎵 Gita - Copyright-Free Music Generator

A simple app to help content creators find copyright-free background music for their videos.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
git clone <your-repo-url>
cd gita
./setup.sh
```

### Option 2: Manual Setup

#### Frontend (React)

```bash
cd frontend
npm install
npm start
```

#### Backend (Python)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api/search-music.py
```

## 🔑 Environment Variables Setup

**Important for Judges:** You need to create a `.env` file in the `backend/` directory with the following API keys to run the application:

### Required Environment Variables

Create a file named `.env` in the `backend/` directory with these variables:

```bash
# Supabase Configuration (Required)
SUPABASE_URL="your_supabase_project_url"
SUPABASE_ANON_KEY="your_supabase_anon_key"

# Groq API Key (Required for AI vision analysis)
GROQ_API_KEY="your_groq_api_key"

# Google Cloud Configuration (Required for Lyria music generation)
PROJECT_ID="your_google_cloud_project_id"
GOOGLE_CLOUD_PROJECT="your_google_cloud_project_id"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_GENAI_USE_VERTEXAI="True"

# Gemini API Key (Alternative AI model)
GEMINI_API_KEY="your_gemini_api_key"

# CORS Configuration (Optional - defaults to http://localhost:3000)
CORS_ORIGINS=http://localhost:3000
```

### Frontend Environment Variables

Create a file named `.env` in the `frontend/` directory:

```bash
# API URL for connecting to backend
REACT_APP_API_URL=http://localhost:8000
```

### How to Get the Required API Keys

1. **Supabase Setup:**

   - Go to [supabase.com](https://supabase.com) and create a new project
   - Navigate to Settings → API
   - Copy the "Project URL" and "anon public" key

2. **Groq API Key:**

   - Visit [console.groq.com](https://console.groq.com)
   - Sign up and create an API key
   - Copy the API key

3. **Google Cloud Project ID:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one
   - Enable the Vertex AI API
   - Set up authentication (run `gcloud auth application-default login`)
   - Copy your Project ID

### Database Setup

You'll also need to create the following tables in your Supabase database:

```sql
-- Videos table
CREATE TABLE videos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  filename TEXT NOT NULL,
  original_filename TEXT,
  file_path TEXT NOT NULL,
  file_size_mb FLOAT,
  duration_seconds FLOAT,
  fps FLOAT,
  resolution TEXT,
  frame_count INTEGER,
  trim_start FLOAT,
  trim_end FLOAT,
  trim_duration FLOAT,
  processing_status TEXT DEFAULT 'uploaded',
  frames_extracted BOOLEAN DEFAULT FALSE,
  vision_analysis TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Music generations table
CREATE TABLE music_generations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  video_id UUID REFERENCES videos(id),
  vision_prompt TEXT,
  music_prompt TEXT,
  music_file_path TEXT,
  music_file_size_mb FLOAT,
  generation_status TEXT DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Storage Buckets

Create these storage buckets in Supabase:

- `videos` - for uploaded video files
- `frames` - for extracted video frames
- `music` - for generated music files
- `final-videos` - for final videos with music

## 🌐 Access the App

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000

### Local Development

1. Clone the repository
2. Run `./setup.sh` for automated setup
3. Start backend: `cd backend && source venv/bin/activate && python server.py`
4. Start frontend: `cd frontend && npm start`
5. Open http://localhost:3000
