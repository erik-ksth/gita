import datetime
import os
import cv2
import tempfile
import requests
import uuid
from typing import List, Dict
from io import BytesIO
from moviepy.editor import VideoFileClip, AudioFileClip
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


def download_video_from_supabase(video_id: str) -> str:
    """
    Download video from Supabase storage to a temporary file.
    
    Args:
        video_id: The UUID of the video in the database
        
    Returns:
        The path to the downloaded temporary video file
    """
    try:
        # Get video metadata from database
        result = supabase.table("videos").select("*").eq("id", video_id).execute()
        
        if not result.data:
            raise Exception(f"Video with ID {video_id} not found in database")
        
        video_metadata = result.data[0]
        file_path = video_metadata["file_path"]
        filename = video_metadata["filename"]
        
        print(f"Downloading video {filename} from Supabase...")
        
        # Download the video file
        response = requests.get(file_path)
        response.raise_for_status()
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        temp_video_path = os.path.join(temp_dir, f"temp_video_{video_id}_{filename}")
        
        with open(temp_video_path, "wb") as f:
            f.write(response.content)
        
        print(f"Video downloaded to: {temp_video_path}")
        return temp_video_path
        
    except Exception as e:
        print(f"Error downloading video from Supabase: {e}")
        raise


def upload_final_video_to_supabase(video_data: bytes, filename: str) -> str:
    """
    Upload final combined video to Supabase storage.
    
    Args:
        video_data: The video file data as bytes
        filename: The filename for the final video
        
    Returns:
        The public URL of the uploaded final video
    """
    try:
        # Upload video to Supabase storage
        result = supabase.storage.from_(STORAGE_BUCKETS["final_videos"]).upload(
            filename, video_data, {"content-type": "video/mp4"}
        )
        
        if result:
            # Get public URL
            public_url = supabase.storage.from_(STORAGE_BUCKETS["final_videos"]).get_public_url(filename)
            print(f"Final video uploaded to Supabase: {filename}")
            return public_url
        else:
            raise Exception("Failed to upload final video to Supabase")
            
    except Exception as e:
        print(f"Error uploading final video to Supabase: {e}")
        raise


def save_final_video_to_database(original_video_id: str, filename: str, file_url: str, 
                                audio_filename: str, final_duration: float, file_size_mb: float) -> str:
    """
    Save final video metadata to Supabase database.
    
    Args:
        original_video_id: The UUID of the original video
        filename: The final video filename
        file_url: The Supabase storage URL
        audio_filename: The audio filename that was combined
        final_duration: The duration of the final video
        file_size_mb: The file size in MB
        
    Returns:
        The final video UUID
    """
    try:
        result = supabase.table("final_videos").insert({
            "original_video_id": original_video_id,
            "filename": filename,
            "file_path": file_url,
            "audio_filename": audio_filename,
            "duration_seconds": final_duration,
            "file_size_mb": file_size_mb,
            "processing_status": "completed"
        }).execute()
        
        if result.data:
            final_video_id = result.data[0]["id"]
            print(f"Final video metadata saved to database: {filename} (ID: {final_video_id})")
            return final_video_id
        else:
            raise Exception("Failed to save final video to database")
            
    except Exception as e:
        print(f"Error saving final video to database: {e}")
        raise


def attach_audio(video_path: str, audio_path: str, fade_out_duration: float = 1.0) -> str:
    """
    Attaches an audio file to a video file using MoviePy with fade out effect.

    Args:
        video_path: The path to the original video file.
        audio_path: The path to the audio file to attach.
        fade_out_duration: Duration in seconds for the audio fade out effect (default: 2.0).

    Returns:
        The path to the final video file with audio.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    print(f"Combining video {video_path} with audio {audio_path}...")
    
    try:
        # Load video and audio clips
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)
        
        # Get video duration
        video_duration = video_clip.duration
        audio_duration = audio_clip.duration
        
        print(f"Video duration: {video_duration:.2f}s, Audio duration: {audio_duration:.2f}s")
        
        # If audio is longer than video, trim it to video length
        if audio_duration > video_duration:
            print(f"Trimming audio to match video duration ({video_duration:.2f}s)")
            audio_clip = audio_clip.subclip(0, video_duration)
        # If video is longer than audio, loop the audio
        elif video_duration > audio_duration:
            print(f"Looping audio to match video duration ({video_duration:.2f}s)")
            # Calculate how many times to loop
            loops_needed = int(video_duration / audio_duration) + 1
            audio_clips = [audio_clip] * loops_needed
            from moviepy.editor import concatenate_audioclips
            looped_audio = concatenate_audioclips(audio_clips)
            audio_clip = looped_audio.subclip(0, video_duration)
        
        # Apply fade out effect to the audio
        if fade_out_duration > 0 and audio_clip.duration > fade_out_duration:
            print(f"Applying fade out effect ({fade_out_duration:.1f}s)")
            audio_clip = audio_clip.fadeout(fade_out_duration)
        
        # Combine video with the new audio (replace existing audio)
        final_video = video_clip.set_audio(audio_clip)
        
        # Generate output filename
        temp_dir = tempfile.gettempdir()
        output_filename = f"final_video_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(temp_dir, output_filename)
        
        # Export the final video
        print(f"Exporting final video to: {output_path}")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=f"{output_path}_temp_audio.m4a",
            remove_temp=True,
            verbose=False,
            logger=None  # Suppress MoviePy logs
        )
        
        # Clean up clips
        video_clip.close()
        audio_clip.close()
        final_video.close()
        
        print(f"Successfully created final video: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error combining video and audio: {e}")
        raise


def download_audio_from_supabase(audio_filename: str) -> str:
    """
    Downloads audio file from Supabase storage.
    
    Args:
        audio_filename: The filename of the audio in Supabase storage
        
    Returns:
        Local path to the downloaded audio file
    """
    try:
        # Get the file from Supabase storage
        response = supabase.storage.from_(STORAGE_BUCKETS["music"]).download(audio_filename)
        
        if not response:
            raise Exception(f"Failed to download audio file: {audio_filename}")
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        temp_audio_path = os.path.join(temp_dir, f"temp_audio_{uuid.uuid4().hex[:8]}.wav")
        
        # Write the downloaded data to temporary file
        with open(temp_audio_path, "wb") as f:
            f.write(response)
        
        print(f"Audio downloaded from Supabase to: {temp_audio_path}")
        return temp_audio_path
        
    except Exception as e:
        print(f"Error downloading audio from Supabase: {e}")
        raise


def combine_video_with_audio_from_supabase(video_id: str, audio_filename: str = None) -> Dict[str, any]:
    """
    Downloads video and audio from Supabase, combines them, and uploads the result back.
    
    Args:
        video_id: The UUID of the video in Supabase
        audio_filename: Optional specific audio filename from Supabase storage (if None, uses test file)
        
    Returns:
        Dictionary containing final video information
    """
    temp_video_path = None
    temp_audio_path = None
    final_video_path = None
    
    try:
        # Download video from Supabase
        temp_video_path = download_video_from_supabase(video_id)
        
        # Handle audio source
        if audio_filename:
            # Download audio from Supabase storage
            temp_audio_path = download_audio_from_supabase(audio_filename)
            print(f"Using generated music from Supabase: {audio_filename}")
        else:
            # Use default test audio file (fallback)
            test_audio_filename = "_Royalty Free Music Rainy Thoughts - Relaxing Lofi Hip Hop Music_160k.mp3"
            audio_path = os.path.join("test", test_audio_filename)
            if not os.path.exists(audio_path):
                # Try absolute path
                audio_path = os.path.join(os.path.dirname(__file__), "..", "test", test_audio_filename)
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Test audio file not found: {test_audio_filename}")
            
            temp_audio_path = audio_path
            audio_filename = test_audio_filename
            print(f"Using test audio file: {audio_path}")
        
        # Combine video with audio
        final_video_path = attach_audio(temp_video_path, temp_audio_path)
        
        # Read final video data
        with open(final_video_path, "rb") as f:
            final_video_data = f.read()
        
        # Generate filename for final video
        final_filename = f"final_video_{video_id}_{uuid.uuid4().hex[:8]}.mp4"
        
        # Upload final video to Supabase
        final_video_url = upload_final_video_to_supabase(final_video_data, final_filename)
        
        # Get video info
        final_video_info = get_video_info(final_video_path)
        
        # Save final video metadata to database
        final_video_id = save_final_video_to_database(
            original_video_id=video_id,
            filename=final_filename,
            file_url=final_video_url,
            audio_filename=audio_filename,
            final_duration=final_video_info["duration_seconds"],
            file_size_mb=final_video_info["file_size_mb"]
        )
        
        return {
            "final_video_id": final_video_id,
            "final_video_url": final_video_url,
            "filename": final_filename,
            "audio_used": audio_filename,
            "duration_seconds": final_video_info["duration_seconds"],
            "file_size_mb": final_video_info["file_size_mb"]
        }
        
    except Exception as e:
        print(f"Error in combine_video_with_audio_from_supabase: {e}")
        raise
        
    finally:
        # Clean up temporary files
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
                print(f"Cleaned up temporary video: {temp_video_path}")
            except:
                pass
        
        if temp_audio_path and os.path.exists(temp_audio_path) and "temp_audio_" in temp_audio_path:
            # Only delete if it's a downloaded file, not the original test file
            try:
                os.remove(temp_audio_path)
                print(f"Cleaned up temporary audio: {temp_audio_path}")
            except:
                pass
        
        if final_video_path and os.path.exists(final_video_path):
            try:
                os.remove(final_video_path)
                print(f"Cleaned up final video: {final_video_path}")
            except:
                pass


video_processing_agent = Agent(
    name="video_processing_agent",
    model="gemini-2.0-flash",
    description="An agent responsible for all video and audio transformations.",
    instruction="You are a helpful agent who can process videos by extracting frames and attaching audio files.",
    tools=[get_video_info, extract_frames, attach_audio, combine_video_with_audio_from_supabase],
) 