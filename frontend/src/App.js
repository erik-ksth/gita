import React, { useState, useRef } from "react";
import VideoTrimModal from "./components/VideoTrimModal";
import "./App.css";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showTrimModal, setShowTrimModal] = useState(false);
  const fileInputRef = useRef(null);

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

      const response = await fetch("http://localhost:8000/upload-video", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
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

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎬 Gita</h1>
        <p>Upload & Trim Your Video (Max 15s)</p>
      </header>

      <main className="App-main">
        <div className="upload-container">
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
        </div>
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
