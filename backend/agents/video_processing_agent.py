import datetime
import os
import cv2
import tempfile
from typing import List, Dict
from io import BytesIO
from google.adk.agents import Agent
from supabase_config import supabase, STORAGE_BUCKETS


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


def upload_frame_to_supabase(frame_data: bytes, filename: str) -> str:
    """
    Upload frame to Supabase storage.
    
    Args:
        frame_data: The frame image data as bytes
        filename: The filename for the frame
        
    Returns:
        The public URL of the uploaded frame
    """
    try:
        # Upload frame to Supabase storage
        result = supabase.storage.from_(STORAGE_BUCKETS["frames"]).upload(
            filename, frame_data, {"content-type": "image/jpeg"}
        )
        
        if result:
            # Get public URL
            public_url = supabase.storage.from_(STORAGE_BUCKETS["frames"]).get_public_url(filename)
            print(f"Frame uploaded to Supabase: {filename}")
            return public_url
        else:
            raise Exception("Failed to upload frame to Supabase")
            
    except Exception as e:
        print(f"Error uploading frame to Supabase: {e}")
        raise


def save_frame_to_database(video_id: str, frame_number: int, timestamp: float, 
                          filename: str, file_path: str, file_size_kb: float) -> str:
    """
    Save frame metadata to Supabase database.
    
    Args:
        video_id: The UUID of the parent video
        frame_number: The frame number (0-indexed)
        timestamp: The timestamp in seconds
        filename: The frame filename
        file_path: The Supabase storage path/URL
        file_size_kb: The file size in KB
        
    Returns:
        The frame UUID
    """
    try:
        result = supabase.table("frames").insert({
            "video_id": video_id,
            "frame_number": frame_number,
            "timestamp_seconds": timestamp,
            "filename": filename,
            "file_path": file_path,
            "file_size_kb": file_size_kb
        }).execute()
        
        if result.data:
            frame_id = result.data[0]["id"]
            print(f"Frame metadata saved to database: {filename} (ID: {frame_id})")
            return frame_id
        else:
            raise Exception("Failed to save frame to database")
            
    except Exception as e:
        print(f"Error saving frame to database: {e}")
        raise


def extract_frames(video_path: str, num_frames: int = 5, video_id: str = None) -> List[str]:
    """
    Extracts exactly num_frames frames from a video file and uploads to Supabase.

    Args:
        video_path: The path to the video file.
        num_frames: Number of frames to extract (default: 5).
        video_id: The UUID of the video in the database.

    Returns:
        A list of public URLs to the extracted frames in Supabase.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
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
    
    frame_urls = []
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
            
            # Convert frame to bytes
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Upload frame to Supabase
            try:
                public_url = upload_frame_to_supabase(frame_bytes, filename)
                frame_urls.append(public_url)
                
                # Save frame metadata to database (if video_id provided)
                if video_id:
                    file_size_kb = len(frame_bytes) / 1024
                    save_frame_to_database(
                        video_id=video_id,
                        frame_number=extracted_count,
                        timestamp=timestamp,
                        filename=filename,
                        file_path=public_url,
                        file_size_kb=file_size_kb
                    )
                
                extracted_count += 1
                print(f"Extracted frame {extracted_count}: {filename}")
                
            except Exception as e:
                print(f"Error processing frame {extracted_count}: {e}")
                continue
                
        else:
            print(f"Warning: Could not extract frame at {timestamp:.2f}s")
    
    cap.release()
    
    print(f"Successfully extracted {len(frame_urls)} frames and uploaded to Supabase")
    return frame_urls


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