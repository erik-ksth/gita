#!/usr/bin/env python3
"""
Comprehensive test suite for all agents in the Gita AI system.
This file contains all testing code that was previously in individual agent files.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))


def test_supabase_connection():
    """Test Supabase connection and configuration."""
    print("=== Supabase Connection Test ===")

    try:
        from supabase_config import supabase, STORAGE_BUCKETS

        print("✅ Supabase client imported successfully")
        print(f"Storage buckets: {STORAGE_BUCKETS}")

        # Test basic connection
        try:
            # Try a simple query to test connection
            result = (
                supabase.table("videos")
                .select("count", count="exact")
                .limit(1)
                .execute()
            )
            print("✅ Supabase connection successful")
        except Exception as e:
            print(f"⚠️ Supabase connection test failed: {e}")

        print("\n=== Supabase Connection Test Complete ===")

    except ImportError as e:
        print(f"Could not import Supabase config: {e}")
    except Exception as e:
        print(f"Error testing Supabase connection: {e}")


def test_video_processor_agent():
    """Test the video processor agent functionality."""
    print("=== Video Processor Agent Test ===")

    try:
        from agents.video_processor_agent import (
            get_video_info,
            extract_frames,
            attach_audio,
        )

        # Test video info function
        print("\n1. Testing video info function")
        test_video_path = "test_video.mp4"  # Replace with actual test video path

        if os.path.exists(test_video_path):
            try:
                video_info = get_video_info(test_video_path)
                print(f"Video info: {video_info}")
            except Exception as e:
                print(f"Error getting video info: {e}")
        else:
            print(f"Test video file not found: {test_video_path}")

        # Test frame extraction function
        print("\n2. Testing frame extraction function")
        if os.path.exists(test_video_path):
            try:
                frames = extract_frames(test_video_path, num_frames=3)
                print(f"Extracted {len(frames)} frames")
            except Exception as e:
                print(f"Error extracting frames: {e}")
        else:
            print(f"Test video file not found: {test_video_path}")

        print("\n=== Video Processor Test Complete ===")

    except ImportError as e:
        print(f"Could not import video processor agent: {e}")
    except Exception as e:
        print(f"Error testing video processor agent: {e}")


def test_prompt_generator_agent():
    """Test the prompt generator agent functionality."""
    print("=== Prompt Generator Agent Test ===")

    try:
        from agents.prompt_generator_agent import analyze_video_frames_from_supabase

        # Test with a video ID (replace with actual video ID from your database)
        test_video_id = "your-test-video-id-here"

        print(f"\n1. Testing vision analysis for video ID: {test_video_id}")
        try:
            result = analyze_video_frames_from_supabase(
                test_video_id, vision_prompt=None
            )
            print(f"Vision analysis result: {result[:100]}...")
        except Exception as e:
            print(f"Error: {e}")

        print("\n=== Prompt Generator Test Complete ===")

    except ImportError as e:
        print(f"Could not import prompt generator agent: {e}")
    except Exception as e:
        print(f"Error testing prompt generator agent: {e}")


def test_prompt_checker_agent():
    """Test the prompt checker agent functionality."""
    print("=== Prompt Checker Agent Test ===")

    try:
        from agents.prompt_checker_agent import (
            validate_and_fix_prompt,
            check_prompt_quality,
        )

        # Test cases
        test_prompts = [
            "Dark Hybrid Film Score, Los Angeles, Studio recording, ominous and relentless. Pristine contemporary Instrumental, recorded live London, Dark Trailer Music. A blend of driving percussive synths, distorted orchestral elements, and filmic pulse textures, with instruments such as synths, distorted strings, brass, and hybrid percussion, and a cinematic approach, featuring pulsing rhythms, dissonant harmonies, and a sense of impending dread, evoking a tense and foreboding atmosphere",
            "bad prompt",
            "Peaceful music with piano and strings",
            "Copyright music from famous artist",
            "Ambient atmospheric music with gentle textures and flowing melodies, suitable for a contemplative scene with natural elements and soft lighting.",
        ]

        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n{i}. Testing prompt: {prompt[:50]}...")
            try:
                result = validate_and_fix_prompt(prompt)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")

        print("\n=== Prompt Checker Test Complete ===")

    except ImportError as e:
        print(f"Could not import prompt checker agent: {e}")
    except Exception as e:
        print(f"Error testing prompt checker agent: {e}")


def test_music_generator_agent():
    """Test the music generator agent functionality."""
    print("=== Music Generation Agent Test ===")

    try:
        from agents.music_generator_agent import (
            generate_music_from_video_id,
            generate_music_with_lyria,
        )

        # Test with a video ID (replace with actual video ID from your database)
        test_video_id = "your-test-video-id-here"

        print(f"\n1. Testing music generation for video ID: {test_video_id}")
        try:
            result1 = generate_music_from_video_id(test_video_id)
            print(f"Generated music URL: {result1}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n2. Testing basic music generation with Lyria")
        try:
            result2 = generate_music_with_lyria(
                prompt="Ambient atmospheric music with gentle textures and flowing melodies",
                negative_prompt="",
                sample_count=1,
            )
            print(f"Generated music file: {result2}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n=== Music Generator Test Complete ===")

    except ImportError as e:
        print(f"Could not import music generator agent: {e}")
    except Exception as e:
        print(f"Error testing music generator agent: {e}")


def test_orchestrator_agent():
    """Test the orchestrator agent workflow."""
    print("=== Orchestrator Agent Test ===")

    try:
        from agents.orchestrator_agent import run_video_to_music_workflow

        # Test with a video ID (replace with actual video ID from your database)
        test_video_id = "your-test-video-id-here"

        print(f"\n1. Testing complete workflow for video ID: {test_video_id}")
        try:
            result = run_video_to_music_workflow(
                video_id=test_video_id,
                vision_prompt="Analyze the visual content and generate a music prompt",
                music_prompt=None,  # Use vision analysis
            )
            print(f"Workflow result: {result}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n=== Orchestrator Test Complete ===")

    except ImportError as e:
        print(f"Could not import orchestrator agent: {e}")
    except Exception as e:
        print(f"Error testing orchestrator agent: {e}")


def test_agent_integration():
    """Test the integration between all agents."""
    print("=== Agent Integration Test ===")

    try:
        from agents import (
            video_processor_agent,
            prompt_generator_agent,
            prompt_checker_agent,
            music_generator_agent,
            run_video_to_music_workflow,
        )

        print("✅ All agents imported successfully")
        print(f"Video processor agent: {video_processor_agent.name}")
        print(f"Prompt generator agent: {prompt_generator_agent.name}")
        print(f"Prompt checker agent: {prompt_checker_agent.name}")
        print(f"Music generator agent: {music_generator_agent.name}")

        print("\n=== Agent Integration Test Complete ===")

    except ImportError as e:
        print(f"Could not import agents: {e}")
    except Exception as e:
        print(f"Error testing agent integration: {e}")


def test_duplicate_frame_handling():
    """Test the duplicate frame handling functionality."""
    print("=== Duplicate Frame Handling Test ===")

    try:
        from agents.video_processor_agent import (
            upload_frame_to_supabase,
            cleanup_existing_frames,
        )

        # Test the upload function with duplicate handling
        print("\n1. Testing duplicate frame upload handling")
        test_frame_data = b"fake_frame_data"  # Mock frame data

        # Try uploading the same filename twice
        filename = "test_frame_duplicate.jpg"

        try:
            # First upload should succeed
            result1 = upload_frame_to_supabase(test_frame_data, filename)
            print(f"First upload successful: {result1}")

            # Second upload should handle duplicate gracefully
            result2 = upload_frame_to_supabase(test_frame_data, filename)
            print(f"Second upload successful (with new name): {result2}")

        except Exception as e:
            print(f"Error testing duplicate upload: {e}")

        print("\n=== Duplicate Frame Handling Test Complete ===")

    except ImportError as e:
        print(f"Could not import video processor agent: {e}")
    except Exception as e:
        print(f"Error testing duplicate frame handling: {e}")


def test_video_length_preservation():
    """Test that the final video maintains the same length as the input video."""
    print("\n=== Testing Video Length Preservation ===")

    try:
        # Test with a sample video (you'll need to provide a test video)
        test_video_path = "test/test_video.mp4"  # Update this path to your test video

        if not os.path.exists(test_video_path):
            print(f"Test video not found: {test_video_path}")
            print("Skipping video length preservation test")
            return

        # Get original video info
        original_info = get_video_info(test_video_path)
        original_duration = original_info["duration_seconds"]
        print(f"Original video duration: {original_duration:.2f}s")

        # Create a test audio file (or use existing one)
        test_audio_path = "test/test_audio.wav"  # Update this path

        if not os.path.exists(test_audio_path):
            print(f"Test audio not found: {test_audio_path}")
            print("Skipping video length preservation test")
            return

        # Combine video with audio
        final_video_path = attach_audio(test_video_path, test_audio_path)

        # Get final video info
        final_info = get_video_info(final_video_path)
        final_duration = final_info["duration_seconds"]
        print(f"Final video duration: {final_duration:.2f}s")

        # Check if durations match (allow small tolerance for encoding)
        duration_diff = abs(final_duration - original_duration)
        tolerance = 0.5  # 0.5 seconds tolerance

        if duration_diff <= tolerance:
            print(
                f"✅ Video length preserved successfully (difference: {duration_diff:.2f}s)"
            )
        else:
            print(f"❌ Video length not preserved (difference: {duration_diff:.2f}s)")
            print(
                f"   Original: {original_duration:.2f}s, Final: {final_duration:.2f}s"
            )

        # Clean up
        if os.path.exists(final_video_path):
            os.remove(final_video_path)
            print(f"Cleaned up test final video: {final_video_path}")

    except Exception as e:
        print(f"❌ Video length preservation test failed: {e}")


def run_all_tests():
    """Run all tests in sequence."""
    print("🚀 Starting Comprehensive Agent Test Suite")
    print("=" * 50)

    # Test Supabase connection first
    test_supabase_connection()

    # Test individual agents
    test_video_processor_agent()
    test_prompt_generator_agent()
    test_prompt_checker_agent()
    test_orchestrator_agent()
    test_music_generator_agent()
    test_duplicate_frame_handling()
    test_video_length_preservation()

    # Test integration
    test_agent_integration()

    print("\n" + "=" * 50)
    print("✅ All tests completed!")


def run_specific_test(test_name: str):
    """Run a specific test by name."""
    test_functions = {
        "prompt_checker": test_prompt_checker_agent,
        "music_generator": test_music_generator_agent,
        "video_processor": test_video_processor_agent,
        "prompt_generator": test_prompt_generator_agent,
        "orchestrator": test_orchestrator_agent,
        "integration": test_agent_integration,
        "supabase": test_supabase_connection,
        "duplicate_frame_handling": test_duplicate_frame_handling,
        "video_length_preservation": test_video_length_preservation,
        "all": run_all_tests,
    }

    if test_name in test_functions:
        print(f"Running {test_name} test...")
        test_functions[test_name]()
    else:
        print(f"Unknown test: {test_name}")
        print(f"Available tests: {', '.join(test_functions.keys())}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test suite for Gita AI agents")
    parser.add_argument(
        "test", nargs="?", default="all", help="Specific test to run (default: all)"
    )

    args = parser.parse_args()

    if args.test == "all":
        run_all_tests()
    else:
        run_specific_test(args.test)
