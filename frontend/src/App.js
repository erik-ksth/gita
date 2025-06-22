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
  const [uploadResult, setUploadResult] = useState(null);
  const [processingStatus, setProcessingStatus] = useState(null);
  const fileInputRef = useRef(null);

  const apiUrl = process.env.REACT_APP_API_URL;

  const genreOptions = [
    { value: "jazz", label: "Jazz", icon: "🎷" },
    { value: "lofi", label: "Lo-Fi", icon: "🎧" },
    { value: "pop", label: "Pop", icon: "🎤" },
    { value: "rock", label: "Rock", icon: "🎸" },
    { value: "hiphop", label: "Hip Hop", icon: "🎵" },
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

      const response = await fetch(`${apiUrl}/upload-video`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadResult(result);
        setProcessingStatus("Processing completed successfully!");
        setCurrentPage("results"); // Navigate to results page
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

  const handleDownload = async (url, filename) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error("Download failed:", error);
      alert("Download failed. Please try again.");
    }
  };

  const renderResultsPage = () => {
    if (!uploadResult) return null;

    return (
      <div className="results-container">
        <div className="results-header">
          <h2>🎉 Your Video is Ready!</h2>
          <p>{processingStatus}</p>
        </div>

        <div className="results-content">
          {/* Processing Summary */}
          <div className="processing-summary">
            <div className="summary-item">
              <span className="summary-label">Original File:</span>
              <span className="summary-value">
                {uploadResult.trim_info?.originalFileName || "N/A"}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Duration:</span>
              <span className="summary-value">
                {uploadResult.trim_info?.duration?.toFixed(1) || "N/A"}s
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Resolution:</span>
              <span className="summary-value">
                {uploadResult.video_info?.resolution || "N/A"}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Frames Extracted:</span>
              <span className="summary-value">
                {uploadResult.extracted_frames?.length || 0}
              </span>
            </div>
          </div>

          {/* Original Video */}
          <div className="video-section">
            <h3>📹 Original Video</h3>
            <div className="video-container">
              <video
                src={uploadResult.file_path}
                controls
                className="result-video"
                preload="metadata"
              >
                Your browser does not support the video tag.
              </video>
              <button
                className="download-btn"
                onClick={() =>
                  handleDownload(
                    uploadResult.file_path,
                    `original_${uploadResult.filename}`
                  )
                }
              >
                📥 Download Original
              </button>
            </div>
          </div>

          {/* Generated Music */}
          {uploadResult.music_generated && uploadResult.music_url && (
            <div className="music-section">
              <h3>🎵 Generated Music</h3>
              <div className="audio-container">
                <audio
                  src={uploadResult.music_url}
                  controls
                  className="result-audio"
                  preload="metadata"
                >
                  Your browser does not support the audio tag.
                </audio>
                <button
                  className="download-btn"
                  onClick={() =>
                    handleDownload(
                      uploadResult.music_url,
                      `music_${uploadResult.video_id}.wav`
                    )
                  }
                >
                  📥 Download Music
                </button>
              </div>
            </div>
          )}

          {/* Final Video with Music */}
          {uploadResult.final_video_created && uploadResult.final_video_url && (
            <div className="final-video-section">
              <h3>🎬 Final Video with Music</h3>
              <div className="video-container final-video">
                <video
                  src={uploadResult.final_video_url}
                  controls
                  className="result-video final"
                  preload="metadata"
                >
                  Your browser does not support the video tag.
                </video>
                <div className="final-video-actions">
                  <button
                    className="download-btn primary"
                    onClick={() =>
                      handleDownload(
                        uploadResult.final_video_url,
                        `final_video_${uploadResult.video_id}.mp4`
                      )
                    }
                  >
                    📥 Download Final Video
                  </button>
                  <button
                    className="share-btn"
                    onClick={() => {
                      if (navigator.share) {
                        navigator.share({
                          title:
                            "My Video with AI-Generated Music. Check it out!",
                          url: uploadResult.final_video_url,
                        });
                      } else {
                        navigator.clipboard.writeText(
                          uploadResult.final_video_url
                        );
                        alert("Video URL copied to clipboard!");
                      }
                    }}
                  >
                    🔗 Share
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="results-actions">
            <button
              className="action-btn secondary"
              onClick={() => {
                setUploadResult(null);
                setProcessingStatus(null);
                setCurrentPage("home");
              }}
            >
              🔄 Process Another Video
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Render current page content
  const renderPageContent = () => {
    switch (currentPage) {
      case "about":
        return <About onNavigate={navigateToPage} />;
      case "contact":
        return <Contact />;
      case "results":
        return renderResultsPage();
      default:
        return (
          <div className="upload-container">
            {/* File Prompt Section */}
            <div className="file-prompt">
              <h2>Upload Your Video</h2>
              <p>
                Drop your video file below to get started with AI-powered music
                generation
              </p>
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
            {/* <div className="genre-selection">
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
            </div> */}
          </div>
        );
    }
  };

  return (
    <div className="App">
      {/* Header Navigation */}
      <nav className="header-nav">
        <div className="header-container">
          <button className="app-brand" onClick={() => navigateToPage("home")}>
            <img src="/Logo.png" alt="GITA Icon" className="app-icon" />
          </button>

          {/* Mobile Menu Button */}
          <button className="mobile-menu-button" onClick={toggleMobileMenu}>
            <span
              className={`hamburger ${isMobileMenuOpen ? "open" : ""}`}
            ></span>
          </button>

          {/* Desktop Navigation */}
          <ul className="nav-menu desktop-nav">
            <li>
              <button
                className={`nav-link ${
                  currentPage === "dashboard" ? "active" : ""
                }`}
                onClick={() => navigateToPage("dashboard")}
              >
                Dashboard
              </button>
            </li>
            <li>
              <button
                className={`nav-link ${
                  currentPage === "about" ? "active" : ""
                }`}
                onClick={() => navigateToPage("about")}
              >
                About
              </button>
            </li>
            <li>
              <button
                className={`nav-link ${
                  currentPage === "contact" ? "active" : ""
                }`}
                onClick={() => navigateToPage("contact")}
              >
                Contact
              </button>
            </li>
          </ul>

          {/* Mobile Navigation Dropdown */}
          <div
            className={`mobile-nav-dropdown ${isMobileMenuOpen ? "open" : ""}`}
          >
            <ul className="nav-menu mobile-nav">
              <li>
                <button
                  className={`nav-link ${
                    currentPage === "dashboard" ? "active" : ""
                  }`}
                  onClick={() => navigateToPage("dashboard")}
                >
                  Dashboard
                </button>
              </li>
              <li>
                <button
                  className={`nav-link ${
                    currentPage === "about" ? "active" : ""
                  }`}
                  onClick={() => navigateToPage("about")}
                >
                  About
                </button>
              </li>
              <li>
                <button
                  className={`nav-link ${
                    currentPage === "contact" ? "active" : ""
                  }`}
                  onClick={() => navigateToPage("contact")}
                >
                  Contact
                </button>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      <main className="App-main">{renderPageContent()}</main>

      {/* Video Trim Modal */}
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
