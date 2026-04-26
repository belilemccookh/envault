"""Encryption and decryption utilities for envault using Fernet symmetric encryption."""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


KEY_FILE = Path.home() / ".envault" / "master.key"
SALT_FILE = Path.home() / ".envault" / "salt"


def _get_or_create_salt() -> bytes:
    """Load existing salt or generate and persist a new one."""
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if SALT_FILE.exists():
        return SALT_FILE.read_bytes()
    salt = os.urandom(16)
    SALT_FILE.write_bytes(salt)
    return salt


def derive_key(passphrase: str) -> bytes:
    """Derive a Fernet-compatible key from a passphrase using PBKDF2."""
    salt = _get_or_create_salt()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))


def get_fernet(passphrase: str) -> Fernet:
    """Return a Fernet instance keyed from the given passphrase."""
    return Fernet(derive_key(passphrase))


def encrypt(data: str, passphrase: str) -> bytes:
    """Encrypt a plaintext string and return ciphertext bytes."""
    return get_fernet(passphrase).encrypt(data.encode())


def decrypt(token: bytes, passphrase: str) -> str:
    """Decrypt ciphertext bytes and return the plaintext string."""
    return get_fernet(passphrase).decrypt(token).decode()
