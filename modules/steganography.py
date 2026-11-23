"""
Steganography Module.

Handles all LSB steganography operations for embedding and extracting
encrypted binary data into lossless PNG images.
"""
import os
import struct
import numpy as np
from PIL import Image

# Magic identifier to ensure we are decoding a StegoGuard image (4 bytes)
MAGIC_IDENTIFIER = b"STG!"
# Version byte (1 byte)
VERSION = 1
# Total header length: 4 (Magic) + 1 (Version) + 4 (Payload length) = 9 bytes
HEADER_LENGTH = 9


class SteganographyError(Exception):
    """Base exception class for steganography errors."""
    pass


class InsufficientCapacityError(SteganographyError):
    """Exception raised when payload exceeds image capacity."""
    pass


class InvalidImageError(SteganographyError):
    """Exception raised when an image is not suitable or supported."""
    pass


class InvalidPayloadError(SteganographyError):
    """Exception raised when the embedded payload is missing or corrupted."""
    pass


def load_image(path: str) -> np.ndarray:
    """
    Loads an image from the given path, ensures it is RGB format.

    Args:
        path (str): File path to the image.

    Returns:
        np.ndarray: The image as a numpy array.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found at {path}")

    try:
        img = Image.open(path)
        # We only support embedding in RGB to avoid transparency or palette issues
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        return np.array(img)
    except Exception as e:
        raise InvalidImageError(f"Failed to load image: {str(e)}")


def save_stego_image(image_array: np.ndarray, output_path: str):
    """
    Saves the numpy array as a lossless PNG image.

    Args:
        image_array (np.ndarray): The image array.
        output_path (str): Path to save the image (must end with .png).
    """
    if not output_path.lower().endswith('.png'):
        raise ValueError("Stego image must be saved as a PNG to avoid compression loss.")
        
    try:
        img = Image.fromarray(image_array.astype('uint8'), 'RGB')
        img.save(output_path, format="PNG")
    except Exception as e:
        raise SteganographyError(f"Failed to save image: {str(e)}")


def calculate_capacity(image_array: np.ndarray) -> int:
    """
    Calculates the maximum number of bytes that can be embedded in the image.
    Uses 1 bit per channel per pixel.

    Args:
        image_array (np.ndarray): The RGB image array.

    Returns:
        int: The maximum payload capacity in bytes (excluding header).
    """
    total_pixels = image_array.shape[0] * image_array.shape[1]
    channels = image_array.shape[2]
    total_bits = total_pixels * channels
    total_bytes = total_bits // 8
    
    # Subtract header size to get usable payload capacity
    capacity = total_bytes - HEADER_LENGTH
    return max(0, capacity)


def embed_data(image_array: np.ndarray, data: bytes) -> np.ndarray:
    """
    Embeds binary data into an RGB image using LSB.

    Args:
        image_array (np.ndarray): The original cover image array.
        data (bytes): The encrypted binary data to embed.

    Returns:
        np.ndarray: A new image array with the embedded data.
    """
    capacity = calculate_capacity(image_array)
    if len(data) > capacity:
        raise InsufficientCapacityError(
            f"Payload size ({len(data)} bytes) exceeds available capacity ({capacity} bytes)."
        )

    # Construct the header
    payload_length = len(data)
    # Header format: 4s B I (4-byte string, 1 unsigned byte, 4-byte unsigned int)
    header = struct.pack(">4s B I", MAGIC_IDENTIFIER, VERSION, payload_length)
    
    full_payload = header + data
    
    # Convert payload to a sequence of bits
    # Using np.unpackbits requires converting bytes to uint8 array first
    payload_array = np.frombuffer(full_payload, dtype=np.uint8)
    payload_bits = np.unpackbits(payload_array)
    
    # Copy the original image to avoid modifying it in place
    stego_array = image_array.copy()
    
    # Flatten the array for easier manipulation
    flat_image = stego_array.flatten()
    
    # Modify the least significant bit
    # Clear the LSB of the selected pixels and set to the payload bits
    num_bits = len(payload_bits)
    flat_image[:num_bits] = (flat_image[:num_bits] & 254) | payload_bits
    
    # Reshape back to original dimensions
    return flat_image.reshape(stego_array.shape)


def extract_data(image_array: np.ndarray) -> bytes:
    """
    Extracts embedded binary data from a stego image.

    Args:
        image_array (np.ndarray): The stego image array.

    Returns:
        bytes: The extracted binary data payload.
    """
    flat_image = image_array.flatten()
    
    # Extract bits from LSB
    extracted_bits = flat_image & 1
    
    # Convert extracted bits to bytes
    # Need to extract enough for the header first to know how much to read
    header_bits_count = HEADER_LENGTH * 8
    if len(extracted_bits) < header_bits_count:
        raise InvalidPayloadError("Image is too small to contain a valid header.")
        
    header_bits = extracted_bits[:header_bits_count]
    header_bytes = np.packbits(header_bits).tobytes()
    
    # Parse header
    try:
        magic, version, payload_length = struct.unpack(">4s B I", header_bytes)
    except struct.error:
        raise InvalidPayloadError("Failed to parse steganography header.")
        
    if magic != MAGIC_IDENTIFIER:
        raise InvalidPayloadError(f"Invalid magic identifier. Found: {magic}")
        
    if version != VERSION:
        raise InvalidPayloadError(f"Unsupported steganography version: {version}")
        
    # Check if payload length makes sense given image size
    total_bits_needed = header_bits_count + payload_length * 8
    if total_bits_needed > len(extracted_bits):
        raise InvalidPayloadError(
            f"Header indicates payload of {payload_length} bytes, but image only has capacity for {(len(extracted_bits) - header_bits_count) // 8} bytes."
        )
        
    # Extract the payload
    payload_bits = extracted_bits[header_bits_count:total_bits_needed]
    payload_bytes = np.packbits(payload_bits).tobytes()
    
    return payload_bytes
