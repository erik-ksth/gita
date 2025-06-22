#!/bin/bash

echo "🎵 Setting up Gita - Copyright-Free Music Finder"
echo "================================================"

# Setup Backend
echo "📦 Setting up Python backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Backend dependencies installed!"

# Setup Frontend
echo "📦 Setting up React frontend..."
cd ../frontend
npm install
echo "✅ Frontend dependencies installed!"

echo ""
echo "🚀 Setup complete! To run the app:"
echo ""
echo "1. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python api/search-music.py"
echo ""
echo "2. Start the frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "🎵 Happy coding!" 