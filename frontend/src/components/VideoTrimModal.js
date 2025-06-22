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
  const [ffmpegError, setFfmpegError] = useState(false);
  const [loadingTimeout, setLoadingTimeout] = useState(false);
  const videoRef = useRef(null);

  const MAX_DURATION = 30; // 30 seconds maximum

  // Load FFmpeg on component mount
  useEffect(() => {
    const loadFFmpeg = async () => {
      try {
        if (!ffmpeg.loaded) {
          console.log("Loading FFmpeg...");

          // Set a timeout for FFmpeg loading
          const loadPromise = ffmpeg.load();
          const timeoutPromise = new Promise((_, reject) =>
            setTimeout(() => reject(new Error("FFmpeg loading timeout")), 10000)
          );

          await Promise.race([loadPromise, timeoutPromise]);
          setFfmpegLoaded(true);
          console.log("FFmpeg loaded successfully");
        }
      } catch (error) {
        console.error("Failed to load FFmpeg:", error);
        setFfmpegLoaded(false);
        setFfmpegError(true);
        // Don't throw error, just set loaded to false so user can skip trimming
      }
    };

    if (isOpen) {
      loadFFmpeg();

      // Show skip option after 5 seconds if FFmpeg hasn't loaded
      const timeoutId = setTimeout(() => {
        if (!ffmpegLoaded) {
          setLoadingTimeout(true);
        }
      }, 5000);

      return () => clearTimeout(timeoutId);
    }
  }, [isOpen, ffmpegLoaded]);

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
      alert(
        "Video processor is still loading. Please wait or use 'Skip Trimming' to upload the original video."
      );
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

  const handleSkipTrimming = () => {
    // Upload original file without trimming
    const videoDurationToUse = Math.min(videoDuration, MAX_DURATION);

    onUpload({
      file: selectedFile, // Send original file
      originalFileName: selectedFile.name,
      trimStart: 0,
      trimEnd: videoDurationToUse,
      duration: videoDurationToUse,
    });
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

  // Show loading screen when uploading or processing
  if (uploading || isProcessing) {
    return (
      <div className="modal-backdrop" onClick={handleModalBackdropClick}>
        <div className="trim-modal">
          <div className="modal-header">
            <h2>Processing Video</h2>
          </div>

          <div className="modal-content">
            <div className="processing-container">
              <div className="processing-status">
                <h3>
                  {isProcessing
                    ? "Trimming Video..."
                    : "Uploading & Processing..."}
                </h3>
                <p>
                  Please wait while we process your video. This may take a few
                  minutes.
                </p>
              </div>

              <div className="progress-container">
                <div className="progress-bar">
                  <div className="progress-fill"></div>
                </div>
                <div className="progress-text">
                  {isProcessing ? "Trimming..." : "Processing..."}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

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
              {!ffmpegLoaded && !ffmpegError && (
                <p className="info-message">
                  Loading video processor...{" "}
                  {loadingTimeout &&
                    "(Taking longer than expected - you can skip trimming)"}
                </p>
              )}
              {ffmpegError && (
                <p className="error-message">
                  ⚠️ Video processor failed to load. You can skip trimming to
                  upload the original video.
                </p>
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

          {/* Show Skip Trimming button if FFmpeg failed to load after some time */}
          {!ffmpegLoaded &&
            videoDuration > 0 &&
            (ffmpegError || loadingTimeout) && (
              <button
                onClick={handleSkipTrimming}
                disabled={uploading || isProcessing}
                className="skip-button"
              >
                {uploading ? "Uploading..." : "Skip Trimming & Upload"}
              </button>
            )}

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
