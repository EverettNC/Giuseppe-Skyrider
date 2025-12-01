"""
MemoryKeeper - Encrypted storage for StillHere.

Photos are sacred. Memories are precious.
They deserve protection with military-grade encryption.

Uses AES-256 encryption (same as Eruptor) to keep your loved ones safe.
Your passphrase is the only key. Lose it, and the memories are gone forever.
This is by design. Security through privacy.
"""

from typing import Optional, Union, Dict, Any, List
from pathlib import Path
import json
from datetime import datetime
import numpy as np
import pickle

from stillhere.core.utils import ImageUtils, VideoUtils
from stillhere.core.encryption import Encryption


class MemoryKeeper:
    """
    Encrypted storage manager for photos and videos.

    Keeps your memories safe with AES-256 encryption.

    Example:
        >>> keeper = MemoryKeeper(encryption_passphrase="your-secret-passphrase")
        >>> keeper.save_photo("photo.jpg", "aunt_mary")
        >>> photo = keeper.load_photo("aunt_mary")
    """

    def __init__(
        self,
        encryption_passphrase: str,
        storage_path: Optional[Union[str, Path]] = None
    ):
        """
        Initialize the MemoryKeeper.

        Args:
            encryption_passphrase: Passphrase for AES-256 encryption
            storage_path: Path to encrypted storage directory (default: ./data)

        Raises:
            ValueError: If passphrase is too weak
        """
        if len(encryption_passphrase) < 12:
            raise ValueError(
                "Passphrase must be at least 12 characters. "
                "These are your precious memories - keep them safe."
            )

        self.passphrase = encryption_passphrase
        self.storage_path = Path(storage_path) if storage_path else Path("data")
        self.storage_path.mkdir(exist_ok=True, parents=True)

        # Initialize encryption
        self.encryption = Encryption(encryption_passphrase)

        # Metadata file (encrypted)
        self.metadata_file = self.storage_path / "memories_metadata.enc"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load encrypted metadata about stored memories."""
        if not self.metadata_file.exists():
            return {}

        try:
            encrypted_data = self.metadata_file.read_bytes()
            decrypted_json = self.encryption.decrypt(encrypted_data)
            return json.loads(decrypted_json)
        except Exception as e:
            print(f"Warning: Could not load metadata: {e}")
            return {}

    def _save_metadata(self):
        """Save encrypted metadata."""
        try:
            json_data = json.dumps(self.metadata, indent=2)
            encrypted_data = self.encryption.encrypt(json_data.encode())
            self.metadata_file.write_bytes(encrypted_data)
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def save_photo(
        self,
        photo: Union[str, Path, np.ndarray],
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Path:
        """
        Save a photo with encryption.

        Args:
            photo: Path to photo or numpy array
            name: Name for the stored photo
            description: Optional description of the photo
            tags: Optional tags for organization

        Returns:
            Path to encrypted photo file
        """
        print(f"🔒 Saving encrypted photo: {name}")

        # Load photo if path provided
        if isinstance(photo, (str, Path)):
            photo_array = ImageUtils.load_image(photo, as_rgb=True)
            original_name = str(photo)
        else:
            photo_array = photo
            original_name = "array"

        # Serialize photo
        photo_bytes = pickle.dumps(photo_array)

        # Encrypt
        encrypted_data = self.encryption.encrypt(photo_bytes)

        # Save to file
        output_path = self.storage_path / f"{name}_photo.enc"
        output_path.write_bytes(encrypted_data)

        # Store metadata
        self.metadata[name] = {
            "type": "photo",
            "description": description,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
            "original_name": original_name,
            "file_path": str(output_path),
            "shape": photo_array.shape
        }
        self._save_metadata()

        print(f"✓ Photo saved and encrypted: {output_path}")
        return output_path

    def load_photo(
        self,
        name: str
    ) -> np.ndarray:
        """
        Load and decrypt a photo.

        Args:
            name: Name of the stored photo

        Returns:
            Photo as numpy array

        Raises:
            FileNotFoundError: If photo doesn't exist
            ValueError: If decryption fails (wrong passphrase)
        """
        if name not in self.metadata:
            raise FileNotFoundError(f"Photo '{name}' not found in storage")

        meta = self.metadata[name]
        if meta.get("type") != "photo":
            raise ValueError(f"'{name}' is not a photo")

        print(f"🔓 Loading encrypted photo: {name}")

        # Load encrypted file
        file_path = Path(meta.get("file_path", self.storage_path / f"{name}_photo.enc"))
        if not file_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {file_path}")

        encrypted_data = file_path.read_bytes()

        # Decrypt
        try:
            photo_bytes = self.encryption.decrypt(encrypted_data)
            photo_array = pickle.loads(photo_bytes)
        except Exception as e:
            raise ValueError(f"Decryption failed. Wrong passphrase? Error: {e}")

        print(f"✓ Photo loaded and decrypted")
        return photo_array

    def save_memory(
        self,
        video: Union[List[np.ndarray], np.ndarray],
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        fps: int = 30
    ) -> Path:
        """
        Save an animated memory (video) with encryption.

        Args:
            video: Video as list of frames or numpy array
            name: Name for the stored memory
            description: Optional description
            tags: Optional tags for organization
            metadata: Optional additional metadata (animation settings, etc.)
            fps: Frames per second

        Returns:
            Path to encrypted video file
        """
        print(f"🔒 Saving encrypted memory: {name}")

        # Convert to list of frames if needed
        if isinstance(video, np.ndarray):
            if len(video.shape) == 4:  # (frames, height, width, channels)
                frames = [video[i] for i in range(video.shape[0])]
            else:
                frames = [video]
        else:
            frames = video

        # Serialize frames
        video_data = {
            "frames": frames,
            "fps": fps,
            "num_frames": len(frames)
        }
        video_bytes = pickle.dumps(video_data)

        # Encrypt
        encrypted_data = self.encryption.encrypt(video_bytes)

        # Save to file
        output_path = self.storage_path / f"{name}_video.enc"
        output_path.write_bytes(encrypted_data)

        # Store metadata
        self.metadata[name] = {
            "type": "video",
            "description": description,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
            "animation_metadata": metadata or {},
            "file_path": str(output_path),
            "num_frames": len(frames),
            "fps": fps
        }
        self._save_metadata()

        print(f"✓ Memory saved and encrypted: {output_path}")
        return output_path

    def load_memory(
        self,
        name: str
    ) -> List[np.ndarray]:
        """
        Load and decrypt an animated memory.

        Args:
            name: Name of the stored memory

        Returns:
            List of video frames

        Raises:
            FileNotFoundError: If memory doesn't exist
            ValueError: If decryption fails
        """
        if name not in self.metadata:
            raise FileNotFoundError(f"Memory '{name}' not found in storage")

        meta = self.metadata[name]
        if meta.get("type") != "video":
            raise ValueError(f"'{name}' is not a video")

        print(f"🔓 Loading encrypted memory: {name}")

        # Load encrypted file
        file_path = Path(meta.get("file_path", self.storage_path / f"{name}_video.enc"))
        if not file_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {file_path}")

        encrypted_data = file_path.read_bytes()

        # Decrypt
        try:
            video_bytes = self.encryption.decrypt(encrypted_data)
            video_data = pickle.loads(video_bytes)
            frames = video_data["frames"]
        except Exception as e:
            raise ValueError(f"Decryption failed. Wrong passphrase? Error: {e}")

        print(f"✓ Memory loaded and decrypted ({len(frames)} frames)")
        return frames

    def export_memory(
        self,
        name: str,
        output_path: Union[str, Path],
        format: str = "mp4"
    ):
        """
        Export a memory to unencrypted video file.

        Use this when you want to share the memory with others.

        Args:
            name: Name of the stored memory
            output_path: Path for exported file
            format: Video format ("mp4", "mov", "avi")
        """
        print(f"📤 Exporting memory '{name}' to {output_path}")
        print("⚠️  Warning: Exported file will NOT be encrypted")

        # Load the encrypted memory
        frames = self.load_memory(name)

        # Get metadata for FPS
        meta = self.metadata[name]
        fps = meta.get("fps", 30)

        # Save as unencrypted video
        VideoUtils.create_video_from_frames(frames, output_path, fps=fps)

        print(f"✓ Memory exported successfully")

    def export_photo(
        self,
        name: str,
        output_path: Union[str, Path]
    ):
        """
        Export a photo to unencrypted image file.

        Args:
            name: Name of the stored photo
            output_path: Path for exported file
        """
        print(f"📤 Exporting photo '{name}' to {output_path}")
        print("⚠️  Warning: Exported file will NOT be encrypted")

        # Load the encrypted photo
        photo = self.load_photo(name)

        # Save as unencrypted image
        ImageUtils.save_image(photo, output_path)

        print(f"✓ Photo exported successfully")

    def list_memories(
        self,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List all stored memories.

        Args:
            memory_type: Filter by type ("photo" or "video")
            tags: Filter by tags

        Returns:
            List of memory metadata
        """
        memories = []

        for name, meta in self.metadata.items():
            # Filter by type
            if memory_type and meta.get("type") != memory_type:
                continue

            # Filter by tags
            if tags:
                if not any(tag in meta.get("tags", []) for tag in tags):
                    continue

            memories.append({
                "name": name,
                **meta
            })

        return memories

    def delete_memory(
        self,
        name: str,
        confirm: bool = False
    ):
        """
        Delete a stored memory.

        This is permanent. The memory will be gone forever.

        Args:
            name: Name of the memory to delete
            confirm: Must be True to actually delete

        Raises:
            ValueError: If confirm is not True
        """
        if not confirm:
            raise ValueError(
                "Deleting memories is permanent. "
                "Set confirm=True to proceed."
            )

        if name not in self.metadata:
            raise FileNotFoundError(f"Memory '{name}' not found")

        print(f"🗑️  Deleting memory: {name}")
        print("   This cannot be undone.")

        # Get file path and delete
        meta = self.metadata[name]
        file_path = Path(meta.get("file_path", ""))
        if file_path.exists():
            file_path.unlink()

        # Remove from metadata
        del self.metadata[name]
        self._save_metadata()

        print(f"✓ Memory deleted permanently")

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about stored memories.

        Returns:
            Dictionary with storage statistics
        """
        total_photos = sum(1 for m in self.metadata.values() if m.get("type") == "photo")
        total_videos = sum(1 for m in self.metadata.values() if m.get("type") == "video")

        # Calculate total storage size
        total_size = 0
        for meta in self.metadata.values():
            file_path = Path(meta.get("file_path", ""))
            if file_path.exists():
                total_size += file_path.stat().st_size

        return {
            "total_memories": len(self.metadata),
            "photos": total_photos,
            "videos": total_videos,
            "storage_path": str(self.storage_path),
            "encrypted": True,
            "encryption_type": "AES-256",
            "total_size_bytes": total_size,
            "total_size_readable": self._format_size(total_size)
        }

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
