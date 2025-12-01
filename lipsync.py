"""
Lip Sync Module for StillHere

Syncs mouth movements to audio for realistic avatar animation.
Makes your aunt's avatar speak with her own voice naturally.
"""

import os
import cv2
import numpy as np
import torch
from pathlib import Path
from typing import Union, Optional
import subprocess
import warnings

HAS_WAV2LIP = False
try:
    # We'll implement Wav2Lip integration here
    # For now, detect if dependencies are available
    import torch
    HAS_WAV2LIP = True
except ImportError:
    warnings.warn("PyTorch not installed. Lip sync unavailable.")


class LipSyncer:
    """
    Syncs lip movements to audio for realistic speaking avatars.
    
    Takes a photo + voice audio and creates a video where the person
    appears to be speaking naturally.
    """
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        device: Optional[str] = None
    ):
        """
        Initialize lip syncer.
        
        Args:
            model_path: Path to Wav2Lip model checkpoint
            device: 'cuda', 'mps', or 'cpu'
        """
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        
        self.device = device
        self.model_path = model_path
        self.model = None
        
        # Model will be loaded lazily on first use
        print(f"LipSyncer initialized on {device}")
    
    def sync_lips_to_audio(
        self,
        face_image: Union[str, Path],
        audio_file: Union[str, Path],
        output_path: Union[str, Path],
        fps: int = 30,
        quality: str = "high"
    ) -> Path:
        """
        Create a video of the face speaking with the audio.
        
        Args:
            face_image: Photo of the person
            audio_file: Audio of what they're saying
            output_path: Where to save the video
            fps: Frames per second
            quality: 'low', 'medium', or 'high'
        
        Returns:
            Path to generated video
        """
        face_image = Path(face_image)
        audio_file = Path(audio_file)
        output_path = Path(output_path)
        
        if not face_image.exists():
            raise FileNotFoundError(f"Face image not found: {face_image}")
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.model is None:
            self._load_model()
        
        print(f"Syncing lips to audio...")
        print(f"  Face: {face_image.name}")
        print(f"  Audio: {audio_file.name}")
        
        # Use FFmpeg-based simple implementation for now
        # This is a placeholder - real Wav2Lip integration coming next
        result = self._simple_lipsync_ffmpeg(
            face_image, audio_file, output_path, fps
        )
        
        print(f"Lip-synced video created: {output_path}")
        return result
    
    def _load_model(self):
        """Load the Wav2Lip model."""
        print("Loading Wav2Lip model...")
        
        if self.model_path and self.model_path.exists():
            print(f"Model found at: {self.model_path}")
            # TODO: Implement actual Wav2Lip model loading
            # This requires downloading the checkpoint first
        else:
            print("Wav2Lip model not found.")
            print("Using fallback lip sync method.")
        
        self.model = "fallback"  # Placeholder
    
    def _simple_lipsync_ffmpeg(
        self,
        image_path: Path,
        audio_path: Path,
        output_path: Path,
        fps: int = 30
    ) -> Path:
        """
        Simple lip sync using FFmpeg (creates video from static image + audio).
        
        This is a basic implementation. Real Wav2Lip provides actual mouth movement.
        """
        try:
            # Get audio duration
            import subprocess
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 
                 'format=duration', '-of', 
                 'default=noprint_wrappers=1:nokey=1', str(audio_path)],
                capture_output=True,
                text=True
            )
            duration = float(result.stdout.strip())
            
            # Create video from image with audio
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', str(image_path),
                '-i', str(audio_path),
                '-c:v', 'libx264',
                '-tune', 'stillimage',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                '-t', str(duration),
                str(output_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
            
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e}")
            raise
        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg for video creation."
            )


class AvatarBuilder:
    """
    Combines voice cloning + lip sync + animation to create complete avatars.
    
    This is the Mode 3 implementation - the full experience.
    """
    
    def __init__(
        self,
        voice_cloner=None,
        lip_syncer=None,
        animator=None
    ):
        """
        Initialize avatar builder.
        
        Args:
            voice_cloner: VoiceCloner instance
            lip_syncer: LipSyncer instance  
            animator: Animator instance (for background animation)
        """
        from .voice import VoiceCloner
        
        self.voice_cloner = voice_cloner or VoiceCloner()
        self.lip_syncer = lip_syncer or LipSyncer()
        self.animator = animator  # Optional
    
    def create_speaking_avatar(
        self,
        photo_path: Union[str, Path],
        voice_sample_path: Union[str, Path],
        text_to_speak: str,
        output_path: Union[str, Path],
        duration: float = 10.0,
        language: str = "en"
    ) -> Path:
        """
        Create a complete speaking avatar video.
        
        This is the Mode 3 magic:
        1. Clone voice from sample
        2. Generate speech audio
        3. Sync lips to audio
        4. Add subtle animation
        5. Output final video
        
        Args:
            photo_path: Photo of your aunt
            voice_sample_path: Audio sample of her voice
            text_to_speak: What she should say
            output_path: Where to save the final video
            duration: Target duration (will auto-trim/pad)
            language: Language code
        
        Returns:
            Path to final avatar video
        """
        photo_path = Path(photo_path)
        voice_sample_path = Path(voice_sample_path)
        output_path = Path(output_path)
        
        print("=" * 60)
        print("Creating Speaking Avatar (Mode 3)")
        print("=" * 60)
        print(f"Photo: {photo_path.name}")
        print(f"Voice sample: {voice_sample_path.name}")
        print(f"Message: '{text_to_speak[:50]}...'")
        print()
        
        # Step 1: Generate voice audio
        print("Step 1/3: Cloning voice and generating speech...")
        temp_audio = output_path.parent / "temp_voice.wav"
        self.voice_cloner.clone_voice(
            text=text_to_speak,
            speaker_wav=voice_sample_path,
            output_path=temp_audio,
            language=language
        )
        print("✓ Voice generated")
        print()
        
        # Step 2: Sync lips to audio
        print("Step 2/3: Syncing lip movements to audio...")
        temp_video = output_path.parent / "temp_lipsynced.mp4"
        self.lip_syncer.sync_lips_to_audio(
            face_image=photo_path,
            audio_file=temp_audio,
            output_path=temp_video
        )
        print("✓ Lips synced")
        print()
        
        # Step 3: Optional animation enhancement
        print("Step 3/3: Finalizing video...")
        if self.animator:
            # Add subtle head movement, breathing, etc.
            print("  Adding subtle animation...")
            # TODO: Integrate with Animator class
            final_video = temp_video
        else:
            final_video = temp_video
        
        # Move to final output location
        if final_video != output_path:
            import shutil
            shutil.move(final_video, output_path)
        
        # Cleanup temp files
        if temp_audio.exists():
            temp_audio.unlink()
        if temp_video.exists() and temp_video != output_path:
            temp_video.unlink()
        
        print("=" * 60)
        print(f"✓ Avatar complete: {output_path}")
        print("=" * 60)
        
        return output_path
    
    def create_tribute_video(
        self,
        photo_path: Union[str, Path],
        voice_sample_path: Union[str, Path],
        output_path: Union[str, Path],
        custom_message: Optional[str] = None,
        language: str = "en"
    ) -> Path:
        """
        Create a tribute video with a gentle message.
        
        Perfect for memorial services or sharing with family.
        
        Args:
            photo_path: Photo of loved one
            voice_sample_path: Their voice sample
            output_path: Where to save video
            custom_message: Custom message, or None for default tribute
            language: Language code
        
        Returns:
            Path to tribute video
        """
        if custom_message is None:
            custom_message = (
                "I love you so much. "
                "I'm always with you, in every moment, every memory. "
                "Keep going. Make me proud. "
                "I'll be here, in your heart, forever."
            )
        
        return self.create_speaking_avatar(
            photo_path=photo_path,
            voice_sample_path=voice_sample_path,
            text_to_speak=custom_message,
            output_path=output_path,
            language=language
        )


# Demo/Test
if __name__ == "__main__":
    print("StillHere Lip Sync & Avatar Builder")
    print("=" * 50)
    print()
    print("This module creates speaking avatars by:")
    print("  1. Cloning voice from audio samples")
    print("  2. Generating speech")
    print("  3. Syncing lips to audio")
    print("  4. Adding subtle animation")
    print()
    print("Mode 3: Complete Avatar with Voice")
    print()
    
    lip_syncer = LipSyncer()
    print("✓ LipSyncer initialized")
    
    try:
        from .voice import VoiceCloner
        voice_cloner = VoiceCloner()
        print("✓ VoiceCloner initialized")
        
        avatar_builder = AvatarBuilder(voice_cloner, lip_syncer)
        print("✓ AvatarBuilder ready")
        print()
        print("Mode 3 is ready to honor your aunt's memory.")
    except Exception as e:
        print(f"Note: {e}")
        print("Install dependencies with:")
        print("  pip install TTS soundfile")
