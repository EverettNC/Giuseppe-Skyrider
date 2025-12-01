"""
Utilities - Image and video processing utilities for StillHere.

Core utilities for loading, saving, and processing photos and videos.
Built with care for precious memories.
"""

from typing import Union, Optional, Tuple, List
from pathlib import Path
import numpy as np
from PIL import Image
import cv2


class ImageUtils:
    """Utilities for image processing."""

    @staticmethod
    def load_image(
        path: Union[str, Path],
        target_size: Optional[Tuple[int, int]] = None,
        as_rgb: bool = True
    ) -> np.ndarray:
        """
        Load an image from file.

        Args:
            path: Path to image file
            target_size: Optional (width, height) to resize to
            as_rgb: Return as RGB (True) or BGR (False)

        Returns:
            Image as numpy array

        Raises:
            FileNotFoundError: If image doesn't exist
            ValueError: If image can't be loaded
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        try:
            # Load with PIL for better format support
            img = Image.open(path)

            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize if requested
            if target_size:
                img = img.resize(target_size, Image.LANCZOS)

            # Convert to numpy array
            img_array = np.array(img)

            # Convert RGB to BGR if requested
            if not as_rgb:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            return img_array

        except Exception as e:
            raise ValueError(f"Failed to load image: {e}")

    @staticmethod
    def save_image(
        image: np.ndarray,
        path: Union[str, Path],
        quality: int = 95
    ):
        """
        Save an image to file.

        Args:
            image: Image as numpy array (RGB or BGR)
            path: Output path
            quality: JPEG quality (1-100)
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to PIL Image
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)

        img = Image.fromarray(image)

        # Save with appropriate quality
        img.save(path, quality=quality, optimize=True)

    @staticmethod
    def resize_image(
        image: np.ndarray,
        size: Tuple[int, int],
        keep_aspect: bool = True
    ) -> np.ndarray:
        """
        Resize an image.

        Args:
            image: Image as numpy array
            size: Target (width, height)
            keep_aspect: Maintain aspect ratio

        Returns:
            Resized image
        """
        h, w = image.shape[:2]
        target_w, target_h = size

        if keep_aspect:
            # Calculate aspect ratio
            aspect = w / h
            target_aspect = target_w / target_h

            if aspect > target_aspect:
                # Width is limiting factor
                new_w = target_w
                new_h = int(target_w / aspect)
            else:
                # Height is limiting factor
                new_h = target_h
                new_w = int(target_h * aspect)

            size = (new_w, new_h)

        # Resize
        img = Image.fromarray(image)
        img = img.resize(size, Image.LANCZOS)
        return np.array(img)

    @staticmethod
    def normalize_image(image: np.ndarray) -> np.ndarray:
        """
        Normalize image to 0-1 range.

        Args:
            image: Image as numpy array

        Returns:
            Normalized image
        """
        if image.dtype == np.uint8:
            return image.astype(np.float32) / 255.0
        return image

    @staticmethod
    def denormalize_image(image: np.ndarray) -> np.ndarray:
        """
        Denormalize image from 0-1 to 0-255 range.

        Args:
            image: Normalized image

        Returns:
            Image as uint8
        """
        if image.dtype == np.float32 or image.dtype == np.float64:
            return (image * 255).astype(np.uint8)
        return image


class VideoUtils:
    """Utilities for video processing."""

    @staticmethod
    def create_video_from_frames(
        frames: List[np.ndarray],
        output_path: Union[str, Path],
        fps: int = 30,
        codec: str = 'mp4v'
    ):
        """
        Create a video from a list of frames.

        Args:
            frames: List of frames as numpy arrays
            output_path: Output video path
            fps: Frames per second
            codec: Video codec ('mp4v', 'avc1', 'h264')
        """
        if not frames:
            raise ValueError("No frames provided")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get frame dimensions
        h, w = frames[0].shape[:2]

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))

        try:
            for frame in frames:
                # Ensure frame is uint8
                if frame.dtype != np.uint8:
                    frame = (frame * 255).astype(np.uint8)

                # Convert RGB to BGR if needed
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                else:
                    frame_bgr = frame

                out.write(frame_bgr)
        finally:
            out.release()

    @staticmethod
    def read_video_frames(
        video_path: Union[str, Path],
        max_frames: Optional[int] = None,
        as_rgb: bool = True
    ) -> List[np.ndarray]:
        """
        Read frames from a video file.

        Args:
            video_path: Path to video file
            max_frames: Maximum number of frames to read
            as_rgb: Return as RGB (True) or BGR (False)

        Returns:
            List of frames as numpy arrays
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        frames = []

        try:
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if as_rgb:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                frames.append(frame)
                frame_count += 1

                if max_frames and frame_count >= max_frames:
                    break
        finally:
            cap.release()

        return frames

    @staticmethod
    def get_video_info(video_path: Union[str, Path]) -> dict:
        """
        Get information about a video file.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video information
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        cap = cv2.VideoCapture(str(video_path))

        try:
            info = {
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
            }
            return info
        finally:
            cap.release()

    @staticmethod
    def add_audio_to_video(
        video_path: Union[str, Path],
        audio_path: Union[str, Path],
        output_path: Union[str, Path]
    ):
        """
        Add audio to a video file.

        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Output path for video with audio

        Note:
            Requires ffmpeg to be installed
        """
        import subprocess

        video_path = Path(video_path)
        audio_path = Path(audio_path)
        output_path = Path(output_path)

        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio not found: {audio_path}")

        # Use ffmpeg to merge
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            str(output_path),
            '-y'  # Overwrite output file
        ]

        subprocess.run(cmd, check=True, capture_output=True)


class FaceUtils:
    """Utilities for face detection and processing."""

    @staticmethod
    def detect_faces(image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image.

        Args:
            image: Image as numpy array

        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        # Use OpenCV's Haar Cascade for basic face detection
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        return [tuple(face) for face in faces]

    @staticmethod
    def crop_face(
        image: np.ndarray,
        bbox: Tuple[int, int, int, int],
        padding: float = 0.2
    ) -> np.ndarray:
        """
        Crop a face from an image with padding.

        Args:
            image: Image as numpy array
            bbox: Bounding box (x, y, w, h)
            padding: Padding factor (0.2 = 20% padding)

        Returns:
            Cropped face image
        """
        x, y, w, h = bbox

        # Add padding
        pad_w = int(w * padding)
        pad_h = int(h * padding)

        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(image.shape[1], x + w + pad_w)
        y2 = min(image.shape[0], y + h + pad_h)

        return image[y1:y2, x1:x2]
