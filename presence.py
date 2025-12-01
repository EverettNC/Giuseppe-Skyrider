"""
Presence - Shared utilities for StillHere and Eruptor.

Because grief and privacy are intertwined.
Because memories deserve protection.
Because presence matters, even after loss.

Shared infrastructure:
- Encryption utilities
- Secure storage
- Privacy protection
- Presence detection
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path


class Presence:
    """
    Shared presence and utility functions.

    Used by both StillHere (memories) and Eruptor (privacy).
    """

    @staticmethod
    def get_timestamp() -> str:
        """
        Get current timestamp in ISO format.

        Returns:
            ISO formatted timestamp
        """
        return datetime.now().isoformat()

    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            path: Path to directory

        Returns:
            Path object
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def get_file_size(path: Path) -> int:
        """
        Get file size in bytes.

        Args:
            path: Path to file

        Returns:
            File size in bytes
        """
        return Path(path).stat().st_size

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    @staticmethod
    def validate_path(path: Path, must_exist: bool = False) -> bool:
        """
        Validate a file path.

        Args:
            path: Path to validate
            must_exist: Whether the path must exist

        Returns:
            True if valid, False otherwise
        """
        try:
            path = Path(path)
            if must_exist and not path.exists():
                return False
            return True
        except Exception:
            return False

    @staticmethod
    def secure_delete(path: Path, passes: int = 3):
        """
        Securely delete a file by overwriting before deletion.

        Args:
            path: Path to file to delete
            passes: Number of overwrite passes (default: 3)
        """
        path = Path(path)
        if not path.exists():
            return

        # Overwrite file content
        file_size = path.stat().st_size
        with open(path, 'wb') as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())

        # Delete file
        path.unlink()

    @staticmethod
    def create_metadata(
        name: str,
        type: str,
        description: Optional[str] = None,
        tags: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create metadata dictionary for stored items.

        Args:
            name: Name of the item
            type: Type of the item (photo, video, etc.)
            description: Optional description
            tags: Optional tags
            **kwargs: Additional metadata

        Returns:
            Metadata dictionary
        """
        metadata = {
            "name": name,
            "type": type,
            "created": Presence.get_timestamp(),
            "description": description,
            "tags": tags or [],
        }
        metadata.update(kwargs)
        return metadata


# Import os for secure_delete
import os
