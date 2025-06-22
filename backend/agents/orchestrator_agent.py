from adk.agent import Sequential
from .video_processing_agent import VideoProcessingAgent
from .vision_analysis_agent import VisionAnalysisAgent
from .music_generation_agent import MusicGenerationAgent


class OrchestratorAgent(Sequential):
    """
    An orchestrator agent that manages the end-to-end workflow
    from video processing to music generation.
    """
    def __init__(self):
        video_agent = VideoProcessingAgent()
        vision_agent = VisionAnalysisAgent()
        music_agent = MusicGenerationAgent()

        # Define the sequence of operations.
        # The ADK's Sequential agent will execute these steps in order.
        # The actual implementation will require passing state between steps.
        super().__init__(
            agents=[
                video_agent,
                vision_agent,
                music_agent,
                video_agent, # Called again to attach audio
            ]
        )

    def run(self, video_path: str, vision_prompt: str, music_prompt: str):
        """
        Executes the entire video-to-music workflow.

        Args:
            video_path: Path to the input video.
            vision_prompt: Custom prompt for the vision analysis.
            music_prompt: Custom prompt for the music generation.
        """
        # In a real implementation, the state would be managed and passed
        # between agent calls. The `Sequential` agent facilitates this.
        # This is a simplified representation of the flow.

        print("Starting workflow...")

        # Step 1: Extract frames
        frames = self.agents[0].extract_frames(video_path=video_path)
        print(f"Frames extracted: {frames}")

        # Step 2: Analyze frames
        description = self.agents[1].analyze_images(
            image_paths=frames, prompt=vision_prompt
        )
        print(f"Scene description: {description}")

        # Step 3: Generate music
        music_file = self.agents[2].generate_music(
            description=description, custom_prompt=music_prompt
        )
        print(f"Music file generated: {music_file}")

        # Step 4: Attach audio to video
        final_video = self.agents[3].attach_audio(
            video_path=video_path, audio_path=music_file
        )
        print(f"Final video created: {final_video}")

        return final_video 