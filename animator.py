"""
Animator - The heart of StillHere.

Brings still photos to life with gentle, respectful animation.
Uses First Order Motion Model (FOMM) and other AI models to create
realistic, dignified movement that honors the person being remembered.

Core Principles:
- Dignity first: No distortion, no caricature
- Quality over speed: Take time to get it right
- Respect the memory: Every frame matters
"""

from typing import Optional, Union, Dict, Any, List
from pathlib import Path
import numpy as np

from stillhere.core.utils import ImageUtils, VideoUtils
from stillhere.models.fomm_wrapper import FOMMModel, get_default_checkpoint_path, get_default_config_path


class AnimationStyle:
    """Predefined animation styles that respect dignity and memory."""

    GENTLE_SMILE = "gentle_smile"
    BREATHING = "breathing"
    HEAD_TURN = "head_turn"
    SPEAKING = "speaking"
    PORTRAIT = "portrait"
    CUSTOM = "custom"

    @classmethod
    def get_all_styles(cls):
        """Return all available animation styles."""
        return [
            cls.GENTLE_SMILE,
            cls.BREATHING,
            cls.HEAD_TURN,
            cls.SPEAKING,
            cls.PORTRAIT,
            cls.CUSTOM
        ]


class Animator:
    """
    Main animation engine for StillHere.

    Transforms still photos into gentle, living memories.

    Example:
        >>> animator = Animator()
        >>> frames = animator.animate(
        ...     photo="path/to/photo.jpg",
        ...     style="gentle_smile",
        ...     duration=5,
        ...     quality="high"
        ... )
        >>> # Save as video
        >>> animator.save_video(frames, "output.mp4")
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "cuda",
        use_cpu: bool = False
    ):
        """
        Initialize the Animator.

        Args:
            model_path: Path to pre-trained models (default: auto-detect)
            device: Device to use ("cuda" or "cpu")
            use_cpu: Force CPU usage even if GPU available
        """
        self.device = "cpu" if use_cpu else device
        self.model = None
        self._initialized = False

        # Auto-detect model paths if not provided
        if model_path is None:
            checkpoint_path = get_default_checkpoint_path()
            config_path = get_default_config_path()
        else:
            checkpoint_path = Path(model_path) / "vox-cpk.pth.tar"
            config_path = Path(model_path) / "vox-256.yaml"

        self.checkpoint_path = checkpoint_path
        self.config_path = config_path

    def _load_model(self):
        """Load the animation model. Lazy loading for faster startup."""
        if self._initialized:
            return

        print("🎬 Initializing animation engine...")

        # Initialize FOMM model
        self.model = FOMMModel(
            checkpoint_path=self.checkpoint_path,
            config_path=self.config_path,
            device=self.device,
            use_demo_mode=True  # Will auto-switch if real models available
        )

        self._initialized = True
        print("✓ Animation engine ready")

    def animate(
        self,
        photo: Union[str, Path, np.ndarray],
        style: str = AnimationStyle.GENTLE_SMILE,
        duration: float = 5.0,
        quality: str = "high",
        fps: int = 30,
        driving_video: Optional[Union[str, Path, List[np.ndarray]]] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> List[np.ndarray]:
        """
        Animate a still photo with the specified style.

        Args:
            photo: Path to photo or numpy array of image
            style: Animation style (see AnimationStyle class)
            duration: Duration in seconds
            quality: Quality level ("low", "medium", "high")
            fps: Frames per second
            driving_video: Optional custom driving video for motion
            output_path: Optional path to save video directly

        Returns:
            List of animated frames

        Raises:
            ValueError: If style is invalid or photo can't be loaded
        """
        self._load_model()

        # Validate style
        if style not in AnimationStyle.get_all_styles():
            raise ValueError(
                f"Invalid style '{style}'. "
                f"Choose from: {AnimationStyle.get_all_styles()}"
            )

        print(f"\n🎨 Creating animation...")
        print(f"   Style: {style}")
        print(f"   Duration: {duration}s at {fps} fps")
        print(f"   Quality: {quality}")

        # Load source image
        if isinstance(photo, (str, Path)):
            print(f"   Loading photo: {photo}")
            source_image = ImageUtils.load_image(photo, as_rgb=True)
        else:
            source_image = photo

        # Resize based on quality
        if quality == "high":
            target_size = (256, 256)
        elif quality == "medium":
            target_size = (128, 128)
        else:
            target_size = (64, 64)

        source_image = ImageUtils.resize_image(source_image, target_size)

        # Calculate number of frames
        num_frames = int(duration * fps)

        # Load driving video if provided
        driving_frames = None
        if driving_video is not None:
            if isinstance(driving_video, (str, Path)):
                print(f"   Loading driving video: {driving_video}")
                driving_frames = VideoUtils.read_video_frames(driving_video)
            else:
                driving_frames = driving_video

        # Animate
        print(f"   Generating {num_frames} frames...")
        frames = self.model.animate(
            source_image=source_image,
            driving_video=driving_frames,
            num_frames=num_frames,
            style=style
        )

        print(f"✓ Animation complete ({len(frames)} frames)")

        # Save if output path provided
        if output_path:
            self.save_video(frames, output_path, fps=fps)

        return frames

    def save_video(
        self,
        frames: List[np.ndarray],
        output_path: Union[str, Path],
        fps: int = 30,
        codec: str = 'mp4v'
    ):
        """
        Save animated frames as a video file.

        Args:
            frames: List of frames
            output_path: Output video path
            fps: Frames per second
            codec: Video codec
        """
        print(f"\n💾 Saving video to: {output_path}")
        VideoUtils.create_video_from_frames(frames, output_path, fps=fps, codec=codec)
        print(f"✓ Video saved successfully")

    def animate_with_voice(
        self,
        photo: Union[str, Path, np.ndarray],
        text: Optional[str] = None,
        voice_sample: Optional[Union[str, Path]] = None,
        audio_file: Optional[Union[str, Path]] = None,
        quality: str = "high",
        fps: int = 30,
        output_path: Optional[Union[str, Path]] = None
    ) -> List[np.ndarray]:
        """
        Animate a photo to speak using voice synthesis or audio.

        Args:
            photo: Path to photo or numpy array of image
            text: Text to speak (requires voice_sample for cloning)
            voice_sample: Sample of person's voice for cloning
            audio_file: Pre-recorded audio to lip-sync to
            quality: Quality level ("low", "medium", "high")
            fps: Frames per second
            output_path: Optional path to save video

        Returns:
            List of animated frames

        Raises:
            ValueError: If neither text+voice_sample nor audio_file provided
        """
        self._load_model()

        if not audio_file and not (text and voice_sample):
            raise ValueError(
                "Must provide either 'audio_file' or both 'text' and 'voice_sample'"
            )

        print("\n🎤 Animating with voice...")
        print("⚠️  Voice synthesis will be available in Phase 3")
        print("   For now, this creates a basic animation")

        if text:
            print(f"   Text: {text}")
        if voice_sample:
            print(f"   Voice sample: {voice_sample}")
        if audio_file:
            print(f"   Audio file: {audio_file}")

        # For now, create basic animation
        # Wav2Lip integration will be added in Phase 3
        frames = self.animate(
            photo=photo,
            style=AnimationStyle.SPEAKING,
            duration=5.0,  # Default duration, will match audio in Phase 3
            quality=quality,
            fps=fps
        )

        if output_path:
            self.save_video(frames, output_path, fps=fps)
            # TODO Phase 3: Add audio to video

        return frames

    def get_style_info(self, style: str) -> Dict[str, Any]:
        """
        Get information about a specific animation style.

        Args:
            style: Animation style name

        Returns:
            Dictionary with style information
        """
        styles_info = {
            AnimationStyle.GENTLE_SMILE: {
                "name": "Gentle Smile",
                "description": "Soft breathing motion with subtle eye blinks and gentle smile",
                "duration": "3-5 seconds",
                "movement": "Minimal",
                "best_for": "Portrait photos, peaceful memories"
            },
            AnimationStyle.BREATHING: {
                "name": "Breathing",
                "description": "Subtle breathing motion, very gentle",
                "duration": "3-10 seconds",
                "movement": "Minimal",
                "best_for": "Creating peaceful, living presence"
            },
            AnimationStyle.HEAD_TURN: {
                "name": "Head Turn",
                "description": "Gentle head turn with natural blinking",
                "duration": "5-10 seconds",
                "movement": "Medium",
                "best_for": "Portrait photos, formal occasions"
            },
            AnimationStyle.SPEAKING: {
                "name": "Speaking",
                "description": "Lip sync to audio with natural head movement",
                "duration": "Matches audio length",
                "movement": "Medium",
                "best_for": "When you have audio or want them to speak"
            },
            AnimationStyle.PORTRAIT: {
                "name": "Portrait",
                "description": "Professional quality with slow head turn and soft smile",
                "duration": "5-10 seconds",
                "movement": "Medium",
                "best_for": "High quality memorial videos"
            },
            AnimationStyle.CUSTOM: {
                "name": "Custom",
                "description": "Use your own driving video for movement",
                "duration": "Matches driving video",
                "movement": "User-defined",
                "best_for": "Full creative control"
            }
        }

        return styles_info.get(style, {})
