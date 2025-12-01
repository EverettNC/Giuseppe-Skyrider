"""
Voice Synthesis Module for StillHere

Creates voice clones from samples to bring memories to life with authentic voice.
For your aunt - so her grandchildren can hear her voice forever.
"""

import os
import torch
import numpy as np
from pathlib import Path
from typing import Optional, List, Union
import warnings

try:
    from TTS.api import TTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    warnings.warn("TTS not installed. Voice cloning unavailable. Install with: pip install TTS")

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False
    warnings.warn("soundfile not installed. Install with: pip install soundfile")


class VoiceCloner:
    """
    Creates voice clones from audio samples.
    
    This allows your aunt's voice to speak new words, bringing memories to life
    with authentic voice that her grandchildren will recognize and cherish.
    """
    
    def __init__(
        self,
        model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2",
        device: Optional[str] = None
    ):
        """
        Initialize voice cloner.
        
        Args:
            model_name: TTS model to use (xtts_v2 supports voice cloning)
            device: 'cuda', 'mps', or 'cpu'. Auto-detected if None.
        """
        if not HAS_TTS:
            raise RuntimeError(
                "TTS library not installed. "
                "Install with: pip install TTS"
            )
        
        if not HAS_SOUNDFILE:
            raise RuntimeError(
                "soundfile library not installed. "
                "Install with: pip install soundfile"
            )
        
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        
        self.device = device
        self.model_name = model_name
        
        print(f"Loading voice cloning model on {device}...")
        print("(This may take a minute on first run)")
        
        try:
            self.tts = TTS(model_name).to(device)
            print("Voice cloning model ready.")
        except Exception as e:
            print(f"Failed to load TTS model: {e}")
            print("Falling back to basic TTS without cloning...")
            # Try a simpler model
            self.tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)
    
    def clone_voice(
        self,
        text: str,
        speaker_wav: Union[str, Path],
        output_path: Union[str, Path],
        language: str = "en",
        emotion: str = "neutral"
    ) -> Path:
        """
        Generate speech in the cloned voice.
        
        Args:
            text: What you want the voice to say
            speaker_wav: Path to audio sample of the voice (5-30 seconds ideal)
            output_path: Where to save the generated audio
            language: Language code (en, es, fr, etc.)
            emotion: Emotional tone (neutral, happy, sad - model dependent)
        
        Returns:
            Path to generated audio file
        """
        speaker_wav = Path(speaker_wav)
        output_path = Path(output_path)
        
        if not speaker_wav.exists():
            raise FileNotFoundError(f"Speaker audio not found: {speaker_wav}")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Synthesizing: '{text[:50]}...' in cloned voice...")
        
        try:
            # Use voice cloning
            self.tts.tts_to_file(
                text=text,
                speaker_wav=str(speaker_wav),
                language=language,
                file_path=str(output_path)
            )
        except TypeError:
            # Fallback for models without speaker_wav support
            print("This model doesn't support voice cloning. Using default voice...")
            self.tts.tts_to_file(
                text=text,
                file_path=str(output_path)
            )
        
        print(f"Voice generated: {output_path}")
        return output_path
    
    def create_tribute_speech(
        self,
        speaker_wav: Union[str, Path],
        output_path: Union[str, Path],
        custom_text: Optional[str] = None,
        language: str = "en"
    ) -> Path:
        """
        Create a gentle tribute message in the loved one's voice.
        
        Args:
            speaker_wav: Audio sample of their voice
            output_path: Where to save the tribute
            custom_text: Custom message, or None for default
            language: Language code
        
        Returns:
            Path to generated tribute audio
        """
        if custom_text is None:
            custom_text = (
                "I love you so much. "
                "I'm always with you, in every moment, every memory. "
                "Keep going. Make me proud. "
                "I'll be here, in your heart, forever."
            )
        
        return self.clone_voice(
            text=custom_text,
            speaker_wav=speaker_wav,
            output_path=output_path,
            language=language
        )
    
    def batch_clone(
        self,
        texts: List[str],
        speaker_wav: Union[str, Path],
        output_dir: Union[str, Path],
        prefix: str = "voice",
        language: str = "en"
    ) -> List[Path]:
        """
        Generate multiple audio clips from one voice sample.
        
        Useful for creating a series of messages.
        
        Args:
            texts: List of text messages to synthesize
            speaker_wav: Voice sample
            output_dir: Directory for output files
            prefix: Filename prefix
            language: Language code
        
        Returns:
            List of paths to generated audio files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        outputs = []
        for i, text in enumerate(texts, 1):
            output_path = output_dir / f"{prefix}_{i:03d}.wav"
            self.clone_voice(
                text=text,
                speaker_wav=speaker_wav,
                output_path=output_path,
                language=language
            )
            outputs.append(output_path)
        
        return outputs
    
    def get_available_languages(self) -> List[str]:
        """Get list of supported languages."""
        if hasattr(self.tts, 'languages'):
            return self.tts.languages
        return ["en"]  # Default fallback
    
    @staticmethod
    def validate_speaker_audio(audio_path: Union[str, Path]) -> dict:
        """
        Check if audio sample is suitable for voice cloning.
        
        Returns:
            Dict with 'valid', 'duration', 'sample_rate', 'message'
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            return {
                'valid': False,
                'message': f"File not found: {audio_path}"
            }
        
        if not HAS_SOUNDFILE:
            return {
                'valid': True,  # Assume valid if we can't check
                'message': "Unable to validate (soundfile not installed)"
            }
        
        try:
            data, sample_rate = sf.read(audio_path)
            duration = len(data) / sample_rate
            
            # Ideal: 5-30 seconds
            if duration < 3:
                message = f"Audio too short ({duration:.1f}s). Ideal: 5-30 seconds."
                valid = False
            elif duration > 60:
                message = f"Audio too long ({duration:.1f}s). Ideal: 5-30 seconds. Will use first 30s."
                valid = True
            else:
                message = f"Audio duration perfect: {duration:.1f}s"
                valid = True
            
            return {
                'valid': valid,
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': data.shape[1] if len(data.shape) > 1 else 1,
                'message': message
            }
        
        except Exception as e:
            return {
                'valid': False,
                'message': f"Failed to read audio: {e}"
            }


class VoiceLibrary:
    """
    Manages multiple voice samples and profiles.
    
    For families with multiple voice recordings to preserve.
    """
    
    def __init__(self, library_path: Union[str, Path]):
        """
        Initialize voice library.
        
        Args:
            library_path: Directory to store voice profiles
        """
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)
        self.profiles_dir = self.library_path / "profiles"
        self.profiles_dir.mkdir(exist_ok=True)
    
    def add_voice_sample(
        self,
        name: str,
        audio_path: Union[str, Path],
        description: Optional[str] = None
    ) -> Path:
        """
        Add a voice sample to the library.
        
        Args:
            name: Profile name (e.g., "Auntie_2023")
            audio_path: Path to audio file
            description: Optional description
        
        Returns:
            Path to stored voice profile
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Create profile directory
        profile_dir = self.profiles_dir / name
        profile_dir.mkdir(exist_ok=True)
        
        # Copy audio file
        import shutil
        dest_audio = profile_dir / f"voice_sample{audio_path.suffix}"
        shutil.copy(audio_path, dest_audio)
        
        # Save metadata
        metadata = {
            'name': name,
            'description': description or f"Voice profile for {name}",
            'audio_file': dest_audio.name,
            'added': str(Path(audio_path).stat().st_mtime)
        }
        
        import json
        metadata_file = profile_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Voice profile '{name}' added to library")
        return profile_dir
    
    def list_profiles(self) -> List[str]:
        """List all voice profiles in library."""
        return [p.name for p in self.profiles_dir.iterdir() if p.is_dir()]
    
    def get_profile_audio(self, name: str) -> Path:
        """Get the audio file for a voice profile."""
        profile_dir = self.profiles_dir / name
        
        if not profile_dir.exists():
            raise ValueError(f"Profile '{name}' not found")
        
        # Look for audio file
        for ext in ['.wav', '.mp3', '.m4a', '.flac']:
            audio_file = profile_dir / f"voice_sample{ext}"
            if audio_file.exists():
                return audio_file
        
        raise FileNotFoundError(f"No audio file found for profile '{name}'")


# Demo/Test function
if __name__ == "__main__":
    print("StillHere Voice Cloning Module")
    print("=" * 50)
    print()
    print("This module clones voices from audio samples")
    print("to preserve the voices of loved ones forever.")
    print()
    
    if HAS_TTS:
        print("✓ TTS installed and ready")
    else:
        print("✗ TTS not installed")
        print("  Install with: pip install TTS")
    
    if HAS_SOUNDFILE:
        print("✓ soundfile installed and ready")
    else:
        print("✗ soundfile not installed")
        print("  Install with: pip install soundfile")
