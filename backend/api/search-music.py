from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Mock music database - in a real app, this would come from a database
MOCK_MUSIC_DB = [
    {
        "title": "Upbeat Adventure",
        "artist": "Creative Commons",
        "genre": "Electronic",
        "duration": "2:45",
        "mood": "energetic",
        "download_url": "https://example.com/upbeat-adventure.mp3"
    },
    {
        "title": "Calm Waters",
        "artist": "Free Music Archive",
        "genre": "Ambient",
        "duration": "3:20",
        "mood": "relaxing",
        "download_url": "https://example.com/calm-waters.mp3"
    },
    {
        "title": "Tech Startup",
        "artist": "CC Mixter",
        "genre": "Corporate",
        "duration": "1:55",
        "mood": "professional",
        "download_url": "https://example.com/tech-startup.mp3"
    },
    {
        "title": "Summer Vibes",
        "artist": "Incompetech",
        "genre": "Pop",
        "duration": "2:30",
        "mood": "happy",
        "download_url": "https://example.com/summer-vibes.mp3"
    },
    {
        "title": "Night Drive",
        "artist": "Free Music Archive",
        "genre": "Synthwave",
        "duration": "4:15",
        "mood": "mysterious",
        "download_url": "https://example.com/night-drive.mp3"
    }
]

@app.route('/api/search-music', methods=['POST'])
def search_music():
    try:
        data = request.get_json()
        query = data.get('query', '').lower()
        
        if not query:
            return jsonify({"results": []})
        
        # Simple search logic - in a real app, you'd use a proper search engine
        results = []
        for track in MOCK_MUSIC_DB:
            if (query in track['title'].lower() or 
                query in track['artist'].lower() or 
                query in track['genre'].lower() or
                query in track['mood'].lower()):
                results.append(track)
        
        # If no exact matches, return all tracks (for demo purposes)
        if not results:
            results = MOCK_MUSIC_DB[:3]  # Return first 3 tracks as suggestions
        
        return jsonify({"results": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Gita API is running!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 