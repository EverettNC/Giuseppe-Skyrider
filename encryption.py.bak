"""
Encryption - AES-256 encryption for StillHere.

Military-grade encryption to protect your most precious memories.

Your passphrase is the only key.
Lose it, and the memories are gone forever.
This is by design. Privacy through security.

Shared encryption infrastructure with Eruptor.
"""

from typing import Union
import hashlib
import os
from pathlib import Path


class Encryption:
    """
    AES-256 encryption utilities.

    Encrypts and decrypts data using a passphrase-derived key.

    Example:
        >>> enc = Encryption("my-secure-passphrase")
        >>> encrypted = enc.encrypt(b"precious data")
        >>> decrypted = enc.decrypt(encrypted)
    """

    def __init__(self, passphrase: str):
        """
        Initialize encryption with a passphrase.

        Args:
            passphrase: The passphrase for encryption/decryption

        Raises:
            ValueError: If passphrase is too weak
        """
        if len(passphrase) < 12:
            raise ValueError(
                "Passphrase must be at least 12 characters for security. "
                "These are your precious memories - protect them well."
            )

        self.passphrase = passphrase
        self._key = None

    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive encryption key from passphrase using PBKDF2.

        Args:
            salt: Salt for key derivation

        Returns:
            32-byte encryption key
        """
        # Use PBKDF2 with 100,000 iterations
        # This makes brute force attacks much harder
        key = hashlib.pbkdf2_hmac(
            'sha256',
            self.passphrase.encode('utf-8'),
            salt,
            100000,
            dklen=32  # 32 bytes = 256 bits
        )
        return key

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data using AES-256.

        Args:
            data: Data to encrypt

        Returns:
            Encrypted data with salt and IV prepended
        """
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import padding
        except ImportError:
            raise ImportError(
                "cryptography library required for encryption. "
                "Install with: pip install cryptography"
            )

        # Generate random salt and IV
        salt = os.urandom(16)  # 16 bytes for salt
        iv = os.urandom(16)    # 16 bytes for IV

        # Derive key from passphrase
        key = self._derive_key(salt)

        # Pad data to block size (128 bits = 16 bytes)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        # Encrypt
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Return: salt + IV + encrypted_data
        return salt + iv + encrypted_data

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data using AES-256.

        Args:
            encrypted_data: Encrypted data (with salt and IV)

        Returns:
            Decrypted data

        Raises:
            ValueError: If decryption fails (wrong passphrase or corrupted data)
        """
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import padding
        except ImportError:
            raise ImportError(
                "cryptography library required for decryption. "
                "Install with: pip install cryptography"
            )

        try:
            # Extract salt, IV, and encrypted data
            salt = encrypted_data[:16]
            iv = encrypted_data[16:32]
            ciphertext = encrypted_data[32:]

            # Derive key from passphrase
            key = self._derive_key(salt)

            # Decrypt
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove padding
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()

            return data

        except Exception as e:
            raise ValueError(
                "Decryption failed. Wrong passphrase or corrupted data. "
                f"Error: {e}"
            )

    def encrypt_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None
    ) -> Path:
        """
        Encrypt a file.

        Args:
            input_path: Path to file to encrypt
            output_path: Path for encrypted file (default: input_path + .enc)

        Returns:
            Path to encrypted file
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        if output_path is None:
            output_path = input_path.with_suffix(input_path.suffix + '.enc')
        else:
            output_path = Path(output_path)

        # Read, encrypt, and write
        data = input_path.read_bytes()
        encrypted_data = self.encrypt(data)
        output_path.write_bytes(encrypted_data)

        return output_path

    def decrypt_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None
    ) -> Path:
        """
        Decrypt a file.

        Args:
            input_path: Path to encrypted file
            output_path: Path for decrypted file (default: removes .enc extension)

        Returns:
            Path to decrypted file

        Raises:
            ValueError: If decryption fails
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        if output_path is None:
            if input_path.suffix == '.enc':
                output_path = input_path.with_suffix('')
            else:
                output_path = input_path.with_suffix('.dec')
        else:
            output_path = Path(output_path)

        # Read, decrypt, and write
        encrypted_data = input_path.read_bytes()
        data = self.decrypt(encrypted_data)
        output_path.write_bytes(data)

        return output_path

    @staticmethod
    def generate_passphrase(length: int = 20) -> str:
        """
        Generate a secure random passphrase.

        Args:
            length: Length of passphrase (default: 20)

        Returns:
            Random passphrase
        """
        import secrets
        import string

        # Use alphanumeric + some special characters
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
        passphrase = ''.join(secrets.choice(alphabet) for _ in range(length))

        return passphrase

    @staticmethod
    def check_passphrase_strength(passphrase: str) -> dict:
        """
        Check the strength of a passphrase.

        Args:
            passphrase: Passphrase to check

        Returns:
            Dictionary with strength analysis
        """
        import string

        length = len(passphrase)
        has_lower = any(c in string.ascii_lowercase for c in passphrase)
        has_upper = any(c in string.ascii_uppercase for c in passphrase)
        has_digit = any(c in string.digits for c in passphrase)
        has_special = any(c in "!@#$%^&*-_=+[]{}|;:,.<>?/" for c in passphrase)

        # Calculate strength score
        score = 0
        if length >= 12:
            score += 1
        if length >= 16:
            score += 1
        if length >= 20:
            score += 1
        if has_lower:
            score += 1
        if has_upper:
            score += 1
        if has_digit:
            score += 1
        if has_special:
            score += 1

        # Determine strength level
        if score >= 6:
            strength = "strong"
        elif score >= 4:
            strength = "moderate"
        else:
            strength = "weak"

        return {
            "strength": strength,
            "score": score,
            "length": length,
            "has_lowercase": has_lower,
            "has_uppercase": has_upper,
            "has_digits": has_digit,
            "has_special": has_special,
            "recommendation": (
                "Excellent passphrase!" if score >= 6
                else "Consider making it longer or more complex"
                if score >= 4
                else "This passphrase is too weak. Use at least 12 characters with mixed case, numbers, and symbols."
            )
        }
