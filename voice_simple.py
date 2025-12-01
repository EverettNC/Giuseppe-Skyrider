"""
Simple Voice Synthesis - Uses OpenAI TTS API (No Compilation Needed)

Avoids the TTS library compilation issues.
Works immediately, no Xcode needed.
"""

import os
from pathlib import Path
from typing import Union, Optional
from openai import OpenAI

class SimpleVoiceCloner:
    """
    Voice synthesis using OpenAI's TTS API.
    Doesn't clone voice exactly, but produces high-quality natural speech.
    Good enough for funeral avatar and customer videos.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key."""
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY required")
        
        self.client = OpenAI(api_key=api_key)
        # Voices: alloy, echo, fable, onyx, nova, shimmer
        # For warm grandmother: nova or shimmer
        self.voice = "nova"
    
    def synthesize_speech(
        self,
        text: str,
        output_path: Union[str, Path],
        voice: Optional[str] = None
    ) -> Path:
        """
        Generate speech from text.
        
        Args:
            text: What to say
            output_path: Where to save audio
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        
        Returns:
            Path to audio file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        voice = voice or self.voice
        
        print(f"Generating speech with {voice} voice...")
        
        response = self.client.audio.speech.create(
            model="tts-1-hd",  # Higher quality
            voice=voice,
            input=text
        )
        
        response.stream_to_file(str(output_path))
        
        print(f"✓ Speech generated: {output_path}")
        return output_path
    
    def create_tribute(
        self,
        output_path: Union[str, Path],
        custom_text: Optional[str] = None
    ) -> Path:
        """Create a gentle tribute message."""
        if custom_text is None:
            custom_text = (
                "I love you so much. "
                "I'm always with you, in every moment, every memory. "
                "Keep going. Make me proud. "
                "I'll be here, in your heart, forever."
            )
        
        return self.synthesize_speech(custom_text, output_path)


# Update companion.py to use this
if __name__ == "__main__":
    print("Simple Voice Synthesis (OpenAI TTS)")
    print("No compilation required!")
    
    try:
        synth = SimpleVoiceCloner()
        print("✓ Ready to generate speech")
    except ValueError as e:
        print(f"✗ {e}")
        print("  Set: export OPENAI_API_KEY='your-key'")
