import datetime
from google.adk.agents import Agent

def generate_music(description: str, custom_prompt: str) -> str:
    """Generates music based on a scene description and a custom prompt.

    Args:
        description: The description of the scene.
        custom_prompt: A custom prompt to guide the music generation.

    Returns:
        The file path to the generated music file.
    """
    # TODO: Implement the interaction with the Lyria API.
    # This will involve passing the combined prompt to the music generation model.
    full_prompt = f"{description}. {custom_prompt}"
    print(f"Generating music with prompt: '{full_prompt}'")
    return "generated_music.mp3"

music_generation_agent = Agent(
    name="music_generation_agent",
    model="gemini-2.0-flash",
    description="An agent that generates music based on a textual description.",
    instruction="You are a helpful agent who can generate music based on scene descriptions and custom prompts.",
    tools=[generate_music],
) 