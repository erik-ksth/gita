import re
import os
from typing import Dict, List, Optional
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def validate_prompt_format(prompt: str) -> Dict[str, any]:
    """
    Validates the format and structure of a music generation prompt.

    Args:
        prompt: The music prompt to validate

    Returns:
        Dictionary with validation results
    """
    validation_result = {"is_valid": True, "issues": [], "suggestions": [], "score": 0}

    # Check if prompt is empty or too short
    if not prompt or len(prompt.strip()) < 20:
        validation_result["is_valid"] = False
        validation_result["issues"].append(
            "Prompt is too short (minimum 20 characters)"
        )
        validation_result["suggestions"].append(
            "Add more descriptive elements about style, instruments, and mood"
        )
        validation_result["score"] -= 30

    # Check if prompt is too long (Lyria has limits)
    if len(prompt) > 500:
        validation_result["is_valid"] = False
        validation_result["issues"].append(
            "Prompt is too long (maximum 500 characters)"
        )
        validation_result["suggestions"].append(
            "Make the prompt more concise while keeping key elements"
        )
        validation_result["score"] -= 20

    # Check for required Lyria format elements
    required_elements = {
        "style": [
            "film score",
            "trailer music",
            "ambient",
            "electronic",
            "orchestral",
            "jazz",
            "rock",
            "pop",
            "classical",
            "folk",
            "world",
            "experimental",
        ],
        "location": [
            "studio",
            "concert hall",
            "outdoor",
            "live",
            "recording",
            "Los Angeles",
            "London",
            "New York",
            "Tokyo",
        ],
        "instruments": [
            "piano",
            "guitar",
            "drums",
            "bass",
            "strings",
            "brass",
            "synths",
            "percussion",
            "violin",
            "cello",
            "trumpet",
            "saxophone",
        ],
        "mood": [
            "peaceful",
            "dramatic",
            "energetic",
            "melancholic",
            "uplifting",
            "dark",
            "bright",
            "mysterious",
            "romantic",
            "tension",
            "relaxing",
        ],
    }

    prompt_lower = prompt.lower()
    found_elements = {}

    for category, keywords in required_elements.items():
        found_keywords = [kw for kw in keywords if kw in prompt_lower]
        found_elements[category] = found_keywords

        if not found_keywords:
            validation_result["issues"].append(f"Missing {category} description")
            validation_result["suggestions"].append(
                f"Add {category} elements to make the prompt more specific"
            )
            validation_result["score"] -= 10
        else:
            validation_result["score"] += 5

    # Check for Lyria-specific format patterns
    lyria_patterns = [
        r"([A-Z][a-z]+)\s+(Film Score|Trailer Music|Background Music)",
        r"(Studio|Live|Concert)\s+recording",
        r"(Pristine|Contemporary|Modern)\s+(Instrumental|Music)",
        r"(featuring|with|including)\s+[a-z\s]+(instruments?|elements?)",
    ]

    pattern_matches = 0
    for pattern in lyria_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            pattern_matches += 1

    if pattern_matches < 2:
        validation_result["issues"].append(
            "Prompt doesn't follow Lyria format guidelines"
        )
        validation_result["suggestions"].append(
            "Follow format: 'Style, Location, Recording type, Pristine/Contemporary Instrumental, featuring instruments and elements'"
        )
        validation_result["score"] -= 5

    # Check for problematic content
    problematic_words = [
        "copyright",
        "trademark",
        "brand",
        "explicit",
        "offensive",
        "inappropriate",
        "illegal",
        "unauthorized",
        "stolen",
        "plagiarized",
        "ripped off",
    ]

    found_problematic = [word for word in problematic_words if word in prompt_lower]
    if found_problematic:
        validation_result["is_valid"] = False
        validation_result["issues"].append(
            f"Contains problematic words: {', '.join(found_problematic)}"
        )
        validation_result["suggestions"].append(
            "Remove references to copyrighted material or inappropriate content"
        )
        validation_result["score"] -= 50

    # Check for special characters that might cause issues
    problematic_chars = ["<", ">", "&", '"', "'", "\\", "/", "|"]
    found_chars = [char for char in problematic_chars if char in prompt]
    if found_chars:
        validation_result["issues"].append(
            f"Contains problematic characters: {', '.join(found_chars)}"
        )
        validation_result["suggestions"].append(
            "Remove special characters that might cause API issues"
        )
        validation_result["score"] -= 10

    # Normalize score to 0-100 range
    validation_result["score"] = max(0, min(100, validation_result["score"] + 50))

    return validation_result


def sanitize_prompt(prompt: str) -> str:
    """
    Sanitizes a prompt by removing problematic content and improving format.

    Args:
        prompt: The raw prompt to sanitize

    Returns:
        The sanitized prompt
    """
    if not prompt:
        return "Ambient atmospheric music with gentle textures and flowing melodies"

    # Remove problematic characters
    sanitized = prompt
    problematic_chars = ["<", ">", "&", '"', "'", "\\", "/", "|"]
    for char in problematic_chars:
        sanitized = sanitized.replace(char, " ")

    # Remove problematic words
    problematic_words = [
        "copyright",
        "trademark",
        "brand",
        "explicit",
        "offensive",
        "inappropriate",
        "illegal",
        "unauthorized",
        "stolen",
        "plagiarized",
        "ripped off",
    ]

    for word in problematic_words:
        sanitized = re.sub(rf"\b{word}\b", "", sanitized, flags=re.IGNORECASE)

    # Clean up extra whitespace
    sanitized = re.sub(r"\s+", " ", sanitized).strip()

    # Ensure it starts with a capital letter
    if sanitized and sanitized[0].islower():
        sanitized = sanitized[0].upper() + sanitized[1:]

    # Add period if missing
    if sanitized and not sanitized.endswith((".", "!", "?")):
        sanitized += "."

    return sanitized


def improve_prompt_structure(prompt: str) -> str:
    """
    Improves the structure of a prompt to better follow Lyria guidelines.

    Args:
        prompt: The prompt to improve

    Returns:
        The improved prompt
    """
    if not prompt:
        return "Ambient atmospheric music with gentle textures and flowing melodies, suitable for contemplative scenes."

    # Check if it already follows good structure
    if re.search(
        r"([A-Z][a-z]+)\s+(Film Score|Trailer Music|Background Music|Music)", prompt
    ):
        return prompt

    # Try to restructure the prompt
    prompt_lower = prompt.lower()

    # Extract key elements
    style_keywords = [
        "ambient",
        "dramatic",
        "peaceful",
        "energetic",
        "melancholic",
        "uplifting",
        "dark",
        "bright",
        "mysterious",
        "romantic",
    ]
    instrument_keywords = [
        "piano",
        "guitar",
        "drums",
        "bass",
        "strings",
        "brass",
        "synths",
        "percussion",
        "violin",
        "cello",
    ]

    found_style = [kw for kw in style_keywords if kw in prompt_lower]
    found_instruments = [kw for kw in instrument_keywords if kw in prompt_lower]

    # Build improved structure
    improved_parts = []

    if found_style:
        style = found_style[0].title()
        improved_parts.append(f"{style} Film Score")
    else:
        improved_parts.append("Contemporary Film Score")

    improved_parts.append("Studio recording")
    improved_parts.append("Pristine contemporary Instrumental")

    if found_instruments:
        instruments = ", ".join(found_instruments[:3])  # Limit to 3 instruments
        improved_parts.append(f"featuring {instruments}")

    # Add the original mood/atmosphere description
    if len(prompt) > 50:
        # Extract the descriptive part
        descriptive_part = prompt.split(",")[-1].strip() if "," in prompt else prompt
        if descriptive_part and len(descriptive_part) > 10:
            improved_parts.append(descriptive_part)

    improved_prompt = ", ".join(improved_parts)

    # Ensure it ends properly
    if not improved_prompt.endswith((".", "!", "?")):
        improved_prompt += "."

    return improved_prompt


def check_prompt_quality(prompt: str) -> Dict[str, any]:
    """
    Comprehensive prompt quality check that validates, sanitizes, and improves prompts.

    Args:
        prompt: The music prompt to check

    Returns:
        Dictionary with validation results and improved prompt
    """
    print(f"Checking prompt quality: {prompt[:100]}...")

    # Step 1: Validate the original prompt
    validation = validate_prompt_format(prompt)

    # Step 2: Sanitize the prompt
    sanitized = sanitize_prompt(prompt)

    # Step 3: Improve structure if needed
    if validation["score"] < 70:
        improved = improve_prompt_structure(sanitized)
    else:
        improved = sanitized

    # Step 4: Validate the improved prompt
    improved_validation = validate_prompt_format(improved)

    result = {
        "original_prompt": prompt,
        "original_validation": validation,
        "sanitized_prompt": sanitized,
        "improved_prompt": improved,
        "improved_validation": improved_validation,
        "final_prompt": (
            improved
            if improved_validation["score"] > validation["score"]
            else sanitized
        ),
        "was_improved": improved_validation["score"] > validation["score"],
        "final_score": max(validation["score"], improved_validation["score"]),
    }

    print(f"Prompt quality check completed. Final score: {result['final_score']}/100")
    if result["was_improved"]:
        print(
            f"Prompt was improved from score {validation['score']} to {improved_validation['score']}"
        )

    return result


def validate_and_fix_prompt(prompt: str) -> str:
    """
    Main function to validate and fix a music prompt.

    Args:
        prompt: The music prompt to validate and fix

    Returns:
        The validated and potentially improved prompt
    """
    try:
        quality_check = check_prompt_quality(prompt)

        if quality_check["final_score"] >= 70:
            print("✅ Prompt passed validation")
            return quality_check["final_prompt"]
        elif quality_check["final_score"] >= 50:
            print("⚠️ Prompt passed with warnings, using improved version")
            return quality_check["final_prompt"]
        else:
            print("❌ Prompt failed validation, using fallback")
            return "Ambient atmospheric music with gentle textures and flowing melodies, suitable for contemplative scenes with natural elements and soft lighting."

    except Exception as e:
        print(f"Error during prompt validation: {e}")
        return (
            "Peaceful background music with subtle ambient tones and gentle melodies."
        )


# Create the ADK agent
prompt_checker_agent = Agent(
    name="prompt_checker_agent",
    model=LiteLlm(model="groq/meta-llama/llama-4-maverick-17b-128e-instruct"),
    description="An agent that validates and improves music generation prompts for Lyria API.",
    instruction="""You are a prompt quality assurance agent. Your TASK is to validate and improve music generation prompts.

    Your responsibilities:
    1. Validate prompts against Lyria AI requirements (https://cloud.google.com/vertex-ai/generative-ai/docs/music/music-gen-prompt-guide)
    2. Check for inappropriate or problematic content
    3. Ensure proper format and structure
    4. Improve prompts that don't meet quality standards
    5. Provide fallback prompts when validation fails

    When checking prompts:
    - Use the `validate_and_fix_prompt` tool to process the input prompt
    - Ensure the prompt follows Lyria format: "Style, Location, Recording type, Pristine/Contemporary Instrumental, featuring instruments and elements"
    - Check for required elements: style, location, instruments, mood
    - Remove any problematic content or characters
    - Provide a high-quality, validated prompt as output

    Always respond with the validated and improved prompt, or explain any issues if the prompt cannot be fixed.
    """,
    tools=[validate_and_fix_prompt, check_prompt_quality],
    output_key="validated_music_prompt",  # Store the validated prompt in session state
)
