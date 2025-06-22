import datetime
import os
import cv2
from typing import List, Dict
from google.adk.agents import Agent


def get_video_info(video_path: str) -> Dict[str, any]:
    """
    Gets metadata information about a video file.

    Args:
        video_path: The path to the video file.

    Returns:
        A dictionary containing video metadata (duration, fps, resolution, etc.)
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0
    
    cap.release()
    
    video_info = {
        "fps": fps,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration_seconds": duration,
        "duration_formatted": f"{int(duration // 60)}:{int(duration % 60):02d}",
        "resolution": f"{width}x{height}",
        "file_size_mb": os.path.getsize(video_path) / (1024 * 1024)
    }
    
    print(f"Video info for {video_path}: {video_info}")
    return video_info


def extract_frames(video_path: str, num_frames: int = 5) -> List[str]:
    """
    Extracts exactly num_frames frames from a video file with equal time intervals.

    Args:
        video_path: The path to the video file.
        num_frames: Number of frames to extract (default: 5).

    Returns:
        A list of file paths to the extracted image frames.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Create frames directory if it doesn't exist
    frames_dir = os.path.join(os.path.dirname(video_path), "frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    # Open the video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    
    # Calculate interval to get exactly num_frames frames
    if duration <= 0:
        cap.release()
        raise ValueError(f"Invalid video duration: {duration}")
    
    # Calculate time interval between frames
    time_interval = duration / num_frames if num_frames > 1 else duration
    
    frame_paths = []
    extracted_count = 0
    
    print(f"Extracting {num_frames} frames from {video_path} (duration: {duration:.2f}s, interval: {time_interval:.2f}s)")
    
    for i in range(num_frames):
        # Calculate the timestamp for this frame
        timestamp = i * time_interval
        
        # Convert timestamp to frame number
        target_frame = int(timestamp * fps)
        
        # Ensure we don't exceed video length
        if target_frame >= frame_count:
            target_frame = frame_count - 1
        
        # Seek to the target frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        
        if ret:
            # Create filename with timestamp
            filename = f"frame_{extracted_count:04d}_t{timestamp:.2f}s.jpg"
            frame_path = os.path.join(frames_dir, filename)
            
            # Save the frame
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            extracted_count += 1
            
            print(f"Extracted frame {extracted_count}: {filename}")
        else:
            print(f"Warning: Could not extract frame at {timestamp:.2f}s")
    
    cap.release()
    
    print(f"Successfully extracted {len(frame_paths)} frames from {video_path}")
    return frame_paths


def attach_audio(video_path: str, audio_path: str) -> str:
    """
    Attaches an audio file to a video file.

    Args:
        video_path: The path to the original video file.
        audio_path: The path to the audio file to attach.

    Returns:
        The path to the final video file with audio.
    """
    # TODO: Implement audio attachment logic using a library like MoviePy or FFmpeg.
    print(f"Attaching {audio_path} to {video_path}.")
    return "final_video.mp4"


video_processing_agent = Agent(
    name="video_processing_agent",
    model="gemini-2.0-flash",
    description="An agent responsible for all video and audio transformations.",
    instruction="You are a helpful agent who can process videos by extracting frames and attaching audio files.",
    tools=[get_video_info, extract_frames, attach_audio],
) 