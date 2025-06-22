import React, { useState, useRef } from "react";
import VideoTrimModal from "./components/VideoTrimModal";
import About from "./components/About";
import Contact from "./components/Contact";
import "./App.css";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showTrimModal, setShowTrimModal] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState("home");
  const [selectedGenre, setSelectedGenre] = useState("jazz");
  const fileInputRef = useRef(null);

  const genreOptions = [
    { value: "jazz", label: "Jazz", icon: "🎷" },
    { value: "lofi", label: "Lo-Fi", icon: "🎧" },
    { value: "pop", label: "Pop", icon: "🎤" },
    { value: "rock", label: "Rock", icon: "🎸" },
    { value: "hiphop", label: "Hip Hop", icon: "🎵" }
  ];

  const handleFileSelect = (file) => {
    if (file && file.type.startsWith("video/")) {
      setSelectedFile(file);
      setShowTrimModal(true);
    } else {
      alert("Please select a valid video file.");
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    handleFileSelect(file);
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleCloseModal = () => {
    setShowTrimModal(false);
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const navigateToPage = (page) => {
    setCurrentPage(page);
    closeMobileMenu();
  };

  const handleUpload = async (trimData) => {
    setUploading(true);
    try {
      const formData = new FormData();

      // Use the trimmed video blob
      formData.append(
        "video",
        trimData.file,
        trimData.originalFileName || "trimmed-video.mp4"
      );
      formData.append("originalFileName", trimData.originalFileName || "");
      formData.append("trimStart", trimData.trimStart);
      formData.append("trimEnd", trimData.trimEnd);
      formData.append("duration", trimData.duration);
      formData.append("genre", selectedGenre);

      const response = await fetch("http://localhost:8000/upload-video", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        //const result = await response.json();
        await response.json();
        // alert("Video uploaded and trimmed successfully!");
        handleCloseModal();
      } else {
        throw new Error("Upload failed");
      }
    } catch (error) {
      console.error("Error uploading video:", error);
      alert("Failed to upload video. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  // Render current page content
  const renderPageContent = () => {
    switch (currentPage) {
      case "about":
        return <About />;
      case "contact":
        return <Contact />;
      default:
        return (
          <div className="upload-container">
            {/* File Prompt Section */}
            <div className="file-prompt">
              <h2>Upload Your Video</h2>
              <p>Drop your video file below to get started with AI-powered music generation</p>
            </div>


            {/* Upload Area */}
            <div
              className={`upload-area ${isDragOver ? "drag-over" : ""}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="upload-content">
                <div className="upload-prompt">
                  <div className="upload-icon">📁</div>
                  <h3>Drop your video here</h3>
                  <p>or click to browse</p>
                  <button
                    className="browse-button"
                    onClick={handleBrowseClick}
                    type="button"
                  >
                    Choose File
                  </button>
                </div>
              </div>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileInputChange}
              style={{ display: "none" }}
            />
            {/* Genre Selection */}
            <div className="genre-selection">
              <label htmlFor="genre-select" className="genre-label">
                Choose Music Genre:
              </label>
              <div className="genre-dropdown">
                <select
                  id="genre-select"
                  value={selectedGenre}
                  onChange={(e) => setSelectedGenre(e.target.value)}
                  className="genre-select"
                >
                  {genreOptions.map((genre) => (
                    <option key={genre.value} value={genre.value}>
                      {genre.icon} {genre.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>


          </div>
        );
    }
  };

  return (
    <div className="App">
      {/* Header Navigation */}
      <nav className="header-nav">
        <div className="header-container">
          <button 
            className="app-brand" 
            onClick={() => navigateToPage("home")}
          >
            <img src="/GITA_1.png" alt="GITA Icon" className="app-icon" />
            <span>GITA</span>
          </button>
          
          {/* Mobile Menu Button */}
          <button className="mobile-menu-button" onClick={toggleMobileMenu}>
            <span className={`hamburger ${isMobileMenuOpen ? 'open' : ''}`}></span>
          </button>
          
          {/* Desktop Navigation */}
          <ul className="nav-menu desktop-nav">
            <li><button 
              className={`nav-link ${currentPage === "dashboard" ? "active" : ""}`}
              onClick={() => navigateToPage("dashboard")}
            >Dashboard</button></li>
            {/* <li><button 
              className={`nav-link ${currentPage === "history" ? "active" : ""}`}
              onClick={() => navigateToPage("history")}
            >History</button></li> */}
            <li><button 
              className={`nav-link ${currentPage === "about" ? "active" : ""}`}
              onClick={() => navigateToPage("about")}
            >About</button></li>
            <li><button 
              className={`nav-link ${currentPage === "contact" ? "active" : ""}`}
              onClick={() => navigateToPage("contact")}
            >Contact</button></li>
          </ul>
          
          {/* Mobile Navigation Dropdown */}
          <div className={`mobile-nav-dropdown ${isMobileMenuOpen ? 'open' : ''}`}>
            <ul className="nav-menu mobile-nav">
              <li><button 
                className={`nav-link ${currentPage === "dashboard" ? "active" : ""}`}
                onClick={() => navigateToPage("dashboard")}
              >Dashboard</button></li>
              {/* <li><button 
                className={`nav-link ${currentPage === "history" ? "active" : ""}`}
                onClick={() => navigateToPage("history")}
              >History</button></li> */}
              <li><button 
                className={`nav-link ${currentPage === "about" ? "active" : ""}`}
                onClick={() => navigateToPage("about")}
              >About</button></li>
              <li><button 
                className={`nav-link ${currentPage === "contact" ? "active" : ""}`}
                onClick={() => navigateToPage("contact")}
              >Contact</button></li>
            </ul>
          </div>
        </div>
      </nav>

      <main className="App-main">
        {renderPageContent()}
      </main>

      <VideoTrimModal
        isOpen={showTrimModal}
        onClose={handleCloseModal}
        selectedFile={selectedFile}
        onUpload={handleUpload}
        uploading={uploading}
      />
    </div>
  );
}

export default App;
