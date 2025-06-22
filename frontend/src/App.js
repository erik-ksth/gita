import React, { useState } from "react";
import "./App.css";

function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [musicResults, setMusicResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const searchMusic = async () => {
    if (!searchTerm.trim()) return;

    setLoading(true);
    try {
      // This will call your Python backend API
      const response = await fetch("http://localhost:8000/search-music", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: searchTerm }),
      });

      const data = await response.json();
      setMusicResults(data.results || []);
    } catch (error) {
      console.error("Error searching music:", error);
      setMusicResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎵 Gita</h1>
        <p>Find Copyright-Free Music for Your Videos</p>
      </header>

      <main className="App-main">
        <div className="search-container">
          <input
            type="text"
            placeholder="Search for music (e.g., 'upbeat', 'calm', 'electronic')"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && searchMusic()}
            className="search-input"
          />
          <button
            onClick={searchMusic}
            disabled={loading}
            className="search-button"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        <div className="results-container">
          {musicResults.length > 0 ? (
            musicResults.map((track, index) => (
              <div key={index} className="music-card">
                <h3>{track.title}</h3>
                <p>Artist: {track.artist}</p>
                <p>Genre: {track.genre}</p>
                <p>Duration: {track.duration}</p>
                <button className="download-button">Download</button>
              </div>
            ))
          ) : (
            <p className="no-results">
              {loading
                ? "Searching for music..."
                : "Search for copyright-free music above"}
            </p>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
