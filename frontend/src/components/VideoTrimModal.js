import React, { useState, useRef, useEffect } from "react";

const VideoTrimModal = ({
  isOpen,
  onClose,
  selectedFile,
  onUpload,
  uploading,
}) => {
  const [videoUrl, setVideoUrl] = useState(null);
  const [videoDuration, setVideoDuration] = useState(0);
  const [trimStart, setTrimStart] = useState(0);
  const [trimEnd, setTrimEnd] = useState(15);
  const [trimmedDuration, setTrimmedDuration] = useState(15);
  const videoRef = useRef(null);

  const MAX_DURATION = 15; // 15 seconds maximum

  useEffect(() => {
    if (isOpen && selectedFile) {
      const url = URL.createObjectURL(selectedFile);
      setVideoUrl(url);
      setTrimStart(0);
      setTrimEnd(MAX_DURATION);
      setTrimmedDuration(MAX_DURATION);
    }
  }, [isOpen, selectedFile]);

  const handleVideoLoad = () => {
    if (videoRef.current) {
      const duration = videoRef.current.duration;
      setVideoDuration(duration);

      // Set initial trim values
      const endTime = Math.min(duration, MAX_DURATION);
      setTrimEnd(endTime);
      setTrimmedDuration(endTime);
    }
  };

  const handleTrimStartChange = (e) => {
    const newStart = parseFloat(e.target.value);
    setTrimStart(newStart);
    setTrimmedDuration(trimEnd - newStart);
  };

  const handleTrimEndChange = (e) => {
    const newEnd = parseFloat(e.target.value);
    setTrimEnd(newEnd);
    setTrimmedDuration(newEnd - trimStart);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleUpload = () => {
    if (trimmedDuration > MAX_DURATION) {
      alert(
        `Video must be ${MAX_DURATION} seconds or less. Current selection: ${trimmedDuration.toFixed(
          1
        )}s`
      );
      return;
    }

    if (trimStart >= trimEnd) {
      alert("Start time must be less than end time.");
      return;
    }

    onUpload({
      file: selectedFile,
      trimStart,
      trimEnd,
      duration: trimmedDuration,
    });
  };

  const handleClose = () => {
    if (videoUrl) {
      URL.revokeObjectURL(videoUrl);
    }
    setVideoUrl(null);
    setVideoDuration(0);
    setTrimStart(0);
    setTrimEnd(15);
    setTrimmedDuration(15);
    onClose();
  };

  const handleModalBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  // Cleanup video URL when component unmounts
  useEffect(() => {
    return () => {
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
      }
    };
  }, [videoUrl]);

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={handleModalBackdropClick}>
      <div className="trim-modal">
        <div className="modal-header">
          <h2>Trim Video</h2>
          <button className="close-button" onClick={handleClose}>
            ✕
          </button>
        </div>

        <div className="modal-content">
          <div className="video-preview">
            <video
              ref={videoRef}
              src={videoUrl}
              controls
              onLoadedMetadata={handleVideoLoad}
            />
          </div>

          <div className="trim-controls">
            <div className="trim-info">
              <p>
                Original: {formatTime(videoDuration)} | Trimmed:{" "}
                {formatTime(trimmedDuration)}
              </p>
              {trimmedDuration > MAX_DURATION && (
                <p className="error-message">
                  ⚠️ Selection exceeds {MAX_DURATION}s limit
                </p>
              )}
            </div>

            <div className="trim-sliders">
              <div className="trim-slider-group">
                <label>Start: {formatTime(trimStart)}</label>
                <input
                  type="range"
                  min="0"
                  max={videoDuration}
                  step="0.1"
                  value={trimStart}
                  onChange={handleTrimStartChange}
                  className="trim-slider"
                />
              </div>

              <div className="trim-slider-group">
                <label>End: {formatTime(trimEnd)}</label>
                <input
                  type="range"
                  min="0"
                  max={videoDuration}
                  step="0.1"
                  value={trimEnd}
                  onChange={handleTrimEndChange}
                  className="trim-slider"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button
            onClick={handleClose}
            className="cancel-button"
            disabled={uploading}
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={
              uploading ||
              trimmedDuration > MAX_DURATION ||
              trimStart >= trimEnd
            }
            className="upload-button"
          >
            {uploading ? "Uploading..." : "Upload & Trim Video"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default VideoTrimModal;
