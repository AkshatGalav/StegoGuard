"""
Verification Module.

Ensures the integrity and authenticity of images and payloads using cryptographic 
SHA-256 hashing and RSA-PSS digital signatures.
"""

import os
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


def calculate_sha256(data: bytes | str) -> str:
    """
    Calculates the SHA-256 hash of binary or text data.

    Args:
        data (bytes or str): Data to hash.

    Returns:
        str: 64-character hexadecimal SHA-256 digest.

    Raises:
        ValueError: If data is None or unsupported format.
    """
    if data is None:
        raise ValueError("Data cannot be None.")
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    elif isinstance(data, (bytes, bytearray)):
        data_bytes = bytes(data)
    else:
        raise ValueError("Data must be bytes or str.")

    return hashlib.sha256(data_bytes).hexdigest()


def calculate_file_hash(path: str) -> str:
    """
    Calculates the SHA-256 hash of a file on disk.

    Args:
        path (str): File path to hash.

    Returns:
        str: 64-character hexadecimal SHA-256 digest.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found at path: {path}")

    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            sha256.update(chunk)

    return sha256.hexdigest()


def generate_signing_keys(key_size: int = 2048) -> tuple[bytes, bytes]:
    """
    Generates an RSA private and public key pair for digital signatures.

    Args:
        key_size (int): Bit length of RSA key (default 2048).

    Returns:
        tuple[bytes, bytes]: (private_key_pem, public_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem


def sign_data(data: bytes | str, private_key_pem: bytes | str) -> bytes:
    """
    Signs data using an RSA private key with PSS padding and SHA-256.

    Args:
        data (bytes or str): Data to sign.
        private_key_pem (bytes or str): PEM-encoded private key.

    Returns:
        bytes: Digital signature bytes.

    Raises:
        ValueError: If key or data is invalid.
    """
    if not data:
        raise ValueError("Data cannot be empty.")
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    else:
        data_bytes = bytes(data)

    if isinstance(private_key_pem, str):
        key_bytes = private_key_pem.encode('utf-8')
    else:
        key_bytes = bytes(private_key_pem)

    try:
        private_key = serialization.load_pem_private_key(key_bytes, password=None)
        signature = private_key.sign(
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    except Exception as e:
        raise ValueError(f"Failed to sign data: {str(e)}")


def verify_signature(data: bytes | str, signature: bytes, public_key_pem: bytes | str) -> bool:
    """
    Verifies an RSA-PSS digital signature against data and a public key.

    Args:
        data (bytes or str): Data to verify.
        signature (bytes): Digital signature bytes.
        public_key_pem (bytes or str): PEM-encoded public key.

    Returns:
        bool: True if signature is valid, False otherwise.
    """
    if not data or not signature or not public_key_pem:
        return False

    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    else:
        data_bytes = bytes(data)

    if isinstance(public_key_pem, str):
        key_bytes = public_key_pem.encode('utf-8')
    else:
        key_bytes = bytes(public_key_pem)

    try:
        public_key = serialization.load_pem_public_key(key_bytes)
        public_key.verify(
            signature,
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except (InvalidSignature, ValueError, Exception):
        return False


def verify_integrity(data: bytes | str, expected_hash: str) -> bool:
    """
    Verifies data integrity by comparing its SHA-256 hash to expected_hash.

    Args:
        data (bytes or str): Data to verify.
        expected_hash (str): Expected SHA-256 hexadecimal hash string.

    Returns:
        bool: True if hashes match, False otherwise.
    """
    if not expected_hash:
        return False
    computed_hash = calculate_sha256(data)
    return computed_hash.lower() == expected_hash.strip().lower()
