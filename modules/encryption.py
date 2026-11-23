"""
Encryption Module.

Handles all cryptographic operations required for securing the secret data before embedding.
Includes functions for generating keys, encrypting data, and decrypting data using AES-256-GCM.
"""
import os
import json
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class EncryptionError(Exception):
    """Base exception class for encryption errors."""
    pass

class DecryptionError(EncryptionError):
    """Exception raised when decryption fails (e.g., tag mismatch, corrupted data)."""
    pass

class InvalidKeyError(EncryptionError):
    """Exception raised when an invalid key is provided."""
    pass

class InvalidDataError(EncryptionError):
    """Exception raised when the encrypted data format is invalid."""
    pass


def generate_key() -> bytes:
    """
    Generates a secure random 256-bit (32 bytes) encryption key for AES-256.
    
    Returns:
        bytes: The 32-byte generated key.
    """
    return get_random_bytes(32)

def save_key_securely(key: bytes, path: str):
    """
    Saves the key securely to the given path.
    
    Args:
        key (bytes): The encryption key.
        path (str): File path to save the key.
    """
    if len(key) != 32:
        raise InvalidKeyError("Key must be 32 bytes for AES-256.")
    
    with open(path, 'wb') as f:
        f.write(key)
        
def load_key_securely(path: str) -> bytes:
    """
    Loads the key securely from the given path.
    
    Args:
        path (str): File path to load the key from.
        
    Returns:
        bytes: The loaded encryption key.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Key file not found at {path}")
        
    with open(path, 'rb') as f:
        key = f.read()
        
    if len(key) != 32:
        raise InvalidKeyError("Loaded key is not 32 bytes in length.")
        
    return key


def encrypt_message(message: str, key: bytes) -> str:
    """
    Encrypts a plaintext message using AES-256-GCM.
    
    Args:
        message (str): The plaintext message to encrypt.
        key (bytes): The 256-bit encryption key.
        
    Returns:
        str: A base64-encoded JSON string containing version, nonce, ciphertext, and tag.
    """
    if not message:
        raise ValueError("Message cannot be empty.")
        
    if len(key) != 32:
        raise InvalidKeyError("Key must be exactly 32 bytes (256 bits).")
        
    try:
        # Generate a random 16-byte nonce
        nonce = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        message_bytes = message.encode('utf-8')
        ciphertext, tag = cipher.encrypt_and_digest(message_bytes)
        
        # Format the data
        encrypted_data = {
            'version': '1.0',
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8')
        }
        
        json_data = json.dumps(encrypted_data)
        return base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
        
    except Exception as e:
        raise EncryptionError(f"Encryption failed: {str(e)}")


def decrypt_message(encrypted_data: str, key: bytes) -> str:
    """
    Decrypts the encrypted data using AES-256-GCM and verifies its integrity.
    
    Args:
        encrypted_data (str): The base64-encoded JSON string containing the encrypted payload.
        key (bytes): The 256-bit decryption key.
        
    Returns:
        str: The decrypted plaintext message.
    """
    if not encrypted_data:
        raise ValueError("Encrypted data cannot be empty.")
        
    if len(key) != 32:
        raise InvalidKeyError("Key must be exactly 32 bytes (256 bits).")
        
    try:
        json_data = base64.b64decode(encrypted_data).decode('utf-8')
        payload = json.loads(json_data)
        
        if payload.get('version') != '1.0':
            raise InvalidDataError("Unsupported encryption version.")
            
        nonce = base64.b64decode(payload['nonce'])
        ciphertext = base64.b64decode(payload['ciphertext'])
        tag = base64.b64decode(payload['tag'])
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext_bytes = cipher.decrypt_and_verify(ciphertext, tag)
        
        return plaintext_bytes.decode('utf-8')
        
    except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as e:
        # MAC check failure throws ValueError in pycryptodome ('MAC check failed')
        if 'MAC check failed' in str(e):
            raise DecryptionError("Authentication failed: Data may be corrupted or key is incorrect.")
        raise InvalidDataError(f"Failed to parse encrypted data: {str(e)}")
    except Exception as e:
        raise DecryptionError(f"Decryption failed: {str(e)}")
