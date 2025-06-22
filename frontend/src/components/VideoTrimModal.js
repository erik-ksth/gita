import React, { useState, useRef, useEffect } from "react";
import { FFmpeg } from "@ffmpeg/ffmpeg";
import { fetchFile } from "@ffmpeg/util";

// Initialize FFmpeg instance
const ffmpeg = new FFmpeg();

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
  const [trimmedVideoBlob, setTrimmedVideoBlob] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [ffmpegLoaded, setFfmpegLoaded] = useState(false);
  const videoRef = useRef(null);

  const MAX_DURATION = 30; // 30 seconds maximum

  // Load FFmpeg on component mount
  useEffect(() => {
    const loadFFmpeg = async () => {
      try {
        if (!ffmpeg.loaded) {
          await ffmpeg.load();
          setFfmpegLoaded(true);
        }
      } catch (error) {
        console.error("Failed to load FFmpeg:", error);
      }
    };

    if (isOpen) {
      loadFFmpeg();
    }
  }, [isOpen]);

  // Trim video using FFmpeg
  const trimVideo = async (videoFile, startTime, endTime) => {
    if (!ffmpegLoaded) {
      throw new Error("FFmpeg not loaded");
    }

    try {
      // Write input file to FFmpeg file system
      const inputFileName = "input.mp4";
      const outputFileName = "output.mp4";

      await ffmpeg.writeFile(inputFileName, await fetchFile(videoFile));

      // Run FFmpeg command to trim video
      await ffmpeg.exec([
        "-i",
        inputFileName,
        "-ss",
        startTime.toString(),
        "-t",
        (endTime - startTime).toString(),
        "-c",
        "copy", // Copy streams without re-encoding for speed
        outputFileName,
      ]);

      // Read the output file
      const data = await ffmpeg.readFile(outputFileName);

      // Create blob from the trimmed video data
      const trimmedBlob = new Blob([data.buffer], { type: "video/mp4" });

      // Clean up
      await ffmpeg.deleteFile(inputFileName);
      await ffmpeg.deleteFile(outputFileName);

      return trimmedBlob;
    } catch (error) {
      console.error("FFmpeg trimming error:", error);
      throw error;
    }
  };

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

  const handleUpload = async () => {
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

    if (!ffmpegLoaded) {
      alert("Video processor is still loading. Please wait.");
      return;
    }

    try {
      setIsProcessing(true);

      // Create trimmed video blob
      const trimmedBlob = await trimVideo(selectedFile, trimStart, trimEnd);
      setTrimmedVideoBlob(trimmedBlob);

      // Send trimmed video to backend
      onUpload({
        file: trimmedBlob, // Send the trimmed blob instead of original file
        originalFileName: selectedFile.name,
        trimStart,
        trimEnd,
        duration: trimmedDuration,
      });
    } catch (error) {
      console.error("Error trimming video:", error);
      alert("Failed to trim video. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClose = () => {
    if (videoUrl) {
      URL.revokeObjectURL(videoUrl);
    }
    if (trimmedVideoBlob) {
      URL.revokeObjectURL(URL.createObjectURL(trimmedVideoBlob));
    }
    setVideoUrl(null);
    setVideoDuration(0);
    setTrimStart(0);
    setTrimEnd(15);
    setTrimmedDuration(15);
    setTrimmedVideoBlob(null);
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
              {!ffmpegLoaded && (
                <p className="info-message">Loading video processor...</p>
              )}
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
            disabled={uploading || isProcessing}
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={
              uploading ||
              isProcessing ||
              !ffmpegLoaded ||
              trimmedDuration > MAX_DURATION ||
              trimStart >= trimEnd
            }
            className="upload-button"
          >
            {!ffmpegLoaded
              ? "Loading..."
              : isProcessing
              ? "Processing..."
              : uploading
              ? "Uploading..."
              : "Upload & Trim Video"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default VideoTrimModal;
