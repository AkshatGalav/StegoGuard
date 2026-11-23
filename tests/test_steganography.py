import os
import struct
import numpy as np
import pytest
from PIL import Image

from modules.steganography import (
    load_image,
    save_stego_image,
    calculate_capacity,
    embed_data,
    extract_data,
    SteganographyError,
    InsufficientCapacityError,
    InvalidImageError,
    InvalidPayloadError,
    MAGIC_IDENTIFIER,
    VERSION,
    HEADER_LENGTH
)

@pytest.fixture
def dummy_image():
    # Create a 100x100 RGB image
    # Capacity: 100 * 100 * 3 / 8 - 9 = 3741 bytes
    img_array = np.zeros((100, 100, 3), dtype=np.uint8)
    return img_array

@pytest.fixture
def temp_image_path(tmp_path):
    path = os.path.join(tmp_path, "test_image.png")
    img = Image.new('RGB', (10, 10), color = 'red')
    img.save(path)
    return path


def test_calculate_capacity(dummy_image):
    capacity = calculate_capacity(dummy_image)
    # (100 * 100 * 3) // 8 - 9 = 3741
    assert capacity == 3741


def test_embed_and_extract_successful(dummy_image):
    payload = b"This is a secret encrypted message."
    
    stego_image = embed_data(dummy_image, payload)
    
    # Ensure original image is not overwritten
    assert not np.array_equal(dummy_image, stego_image)
    
    extracted_payload = extract_data(stego_image)
    assert extracted_payload == payload


def test_embed_and_extract_small_payload(dummy_image):
    payload = b"X"
    stego_image = embed_data(dummy_image, payload)
    extracted_payload = extract_data(stego_image)
    assert extracted_payload == payload


def test_embed_and_extract_large_payload(dummy_image):
    # Create a payload just at the limit
    capacity = calculate_capacity(dummy_image)
    payload = os.urandom(capacity)
    
    stego_image = embed_data(dummy_image, payload)
    extracted_payload = extract_data(stego_image)
    assert extracted_payload == payload


def test_insufficient_capacity(dummy_image):
    capacity = calculate_capacity(dummy_image)
    payload = os.urandom(capacity + 1)
    
    with pytest.raises(InsufficientCapacityError):
        embed_data(dummy_image, payload)


def test_invalid_magic_identifier(dummy_image):
    payload = b"Secret"
    stego_image = embed_data(dummy_image, payload)
    
    # Corrupt the magic identifier
    flat = stego_image.flatten()
    # Let's just flip the first bit
    flat[0] = flat[0] ^ 1
    corrupted_image = flat.reshape(stego_image.shape)
    
    with pytest.raises(InvalidPayloadError, match="Invalid magic identifier"):
        extract_data(corrupted_image)


def test_invalid_version(dummy_image):
    payload = b"Secret"
    stego_image = embed_data(dummy_image, payload)
    
    # Version is the 5th byte in the header. Each byte takes 8 bits.
    # So version starts at bit index 32
    flat = stego_image.flatten()
    # Let's change the version byte by flipping the first bit of it (bit index 32)
    flat[32] = flat[32] ^ 1
    corrupted_image = flat.reshape(stego_image.shape)
    
    with pytest.raises(InvalidPayloadError, match="Unsupported steganography version"):
        extract_data(corrupted_image)


def test_corrupted_payload_length_too_large(dummy_image):
    payload = b"Secret"
    stego_image = embed_data(dummy_image, payload)
    
    # Payload length is from bit index 40 to 71
    # Let's set a bit in the higher order of payload length to make it huge
    flat = stego_image.flatten()
    flat[40] = 1 # Flip to 1, this represents a huge number if MSB
    corrupted_image = flat.reshape(stego_image.shape)
    
    with pytest.raises(InvalidPayloadError, match="Header indicates payload of"):
        extract_data(corrupted_image)


def test_load_image(temp_image_path):
    img_array = load_image(temp_image_path)
    assert img_array.shape == (10, 10, 3)


def test_load_image_invalid_path():
    with pytest.raises(FileNotFoundError):
        load_image("non_existent_file.png")


def test_save_stego_image(dummy_image, tmp_path):
    output_path = os.path.join(tmp_path, "output.png")
    save_stego_image(dummy_image, output_path)
    assert os.path.exists(output_path)


def test_save_stego_image_invalid_extension(dummy_image, tmp_path):
    output_path = os.path.join(tmp_path, "output.jpg")
    with pytest.raises(ValueError, match="Stego image must be saved as a PNG"):
        save_stego_image(dummy_image, output_path)
