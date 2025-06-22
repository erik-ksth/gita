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
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Groq API Key (Required for AI vision analysis)
GROQ_API_KEY=your_groq_api_key

# Google Cloud Project ID (Required for Lyria music generation)
PROJECT_ID=your_google_cloud_project_id

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

## 📁 Project Structure

```
gita/
├── frontend/          # React app
│   ├── src/
│   ├── package.json
│   └── vercel.json
├── backend/           # Python API
│   ├── api/
│   ├── requirements.txt
│   └── vercel.json
├── setup.sh          # Automated setup script
├── .gitignore        # Git ignore rules
└── README.md
```

## 🌐 Access the App

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Health Check:** http://localhost:8000/api/health

## 🚀 Deployment

### Option 1: Separate Deployments (Recommended for Hackathons)

1. **Deploy Backend to Vercel:**

   ```bash
   cd backend
   vercel
   ```

2. **Deploy Frontend to Vercel:**
   ```bash
   cd frontend
   # Update the API URL in vercel.json with your backend URL
   vercel
   ```

### Option 2: Monorepo Deployment

Deploy both together by placing them in a single Vercel project.

## ✨ Features

- 🔍 Search for music by genre, mood, or keywords
- 📱 Responsive design for mobile and desktop
- 🎵 Mock database with sample tracks
- ⚡ Fast API responses
- 🎨 Modern, clean UI

## 🔧 API Endpoints

- `POST /api/search-music` - Search for music tracks
- `GET /api/health` - Health check endpoint

## 📝 Example API Response

```json
{
  "results": [
    {
      "title": "Upbeat Adventure",
      "artist": "Creative Commons",
      "genre": "Electronic",
      "duration": "2:45",
      "mood": "energetic",
      "download_url": "https://example.com/upbeat-adventure.mp3"
    }
  ]
}
```

## 🛠️ Development

### Prerequisites

- Node.js (v14 or higher)
- Python 3.8+
- npm or yarn

### Local Development

1. Clone the repository
2. Run `./setup.sh` for automated setup
3. Start backend: `cd backend && source venv/bin/activate && python api/search-music.py`
4. Start frontend: `cd frontend && npm start`
5. Open http://localhost:3000

## 🚀 Next Steps

1. Connect to a real music database (e.g., Free Music Archive API)
2. Add audio preview functionality
3. Implement user accounts and favorites
4. Add music filtering by duration, BPM, etc.
5. Integrate with video editing platforms

## 🛠️ Tech Stack

- **Frontend:** React, CSS3
- **Backend:** Python, Flask
- **Deployment:** Vercel
- **API:** RESTful endpoints

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
