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
