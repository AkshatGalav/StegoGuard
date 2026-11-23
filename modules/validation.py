"""
Validation Module.

Provides file, image, and cryptographic payload validation logic to ensure safe,
un-corrupted file handling and prevent security vulnerabilities.
"""

import io
from PIL import Image

ALLOWED_IMAGE_FORMATS = ('PNG', 'JPEG', 'JPG', 'BMP', 'TIFF')
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_uploaded_image(
    file_bytes: bytes,
    filename: str = None,
    max_size_bytes: int = MAX_IMAGE_SIZE_BYTES,
    allowed_formats: tuple = ALLOWED_IMAGE_FORMATS
) -> dict:
    """
    Validates uploaded image bytes for file size, format extension, and content integrity.

    Args:
        file_bytes (bytes): Binary bytes of the uploaded image file.
        filename (str, optional): Name of the uploaded file for extension validation.
        max_size_bytes (int): Maximum allowable file size in bytes (default 10MB).
        allowed_formats (tuple): Allowed PIL image formats.

    Returns:
        dict: Metadata dictionary containing image properties ('format', 'width', 'height', 'mode', 'size_bytes').

    Raises:
        ValueError: If file is empty, oversize, corrupt, or unsupported format.
    """
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    file_size = len(file_bytes)
    if file_size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        raise ValueError(f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum limit of {max_mb:.1f} MB.")

    if filename:
        ext = filename.rsplit('.', 1)[-1].upper() if '.' in filename else ''
        valid_exts = set(f.upper() for f in allowed_formats)
        if 'JPEG' in valid_exts:
            valid_exts.add('JPG')
        if 'JPG' in valid_exts:
            valid_exts.add('JPEG')

        if ext and ext not in valid_exts:
            raise ValueError(f"File extension '.{ext.lower()}' is not supported. Allowed formats: {', '.join(allowed_formats)}.")

    # Content Integrity Verification via Pillow
    try:
        image_stream = io.BytesIO(file_bytes)
        img = Image.open(image_stream)
        img.verify()  # Verifies file header and block structure integrity
    except Exception as e:
        raise ValueError(f"Corrupt or invalid image file content: {str(e)}")

    # Re-open stream after verify() to inspect metadata
    try:
        image_stream.seek(0)
        img = Image.open(image_stream)
        fmt = img.format.upper() if img.format else ''

        valid_fmts = set(f.upper() for f in allowed_formats)
        if 'JPEG' in valid_fmts:
            valid_fmts.add('JPG')

        if fmt not in valid_fmts:
            raise ValueError(f"Image format '{fmt}' is not supported. Allowed formats: {', '.join(allowed_formats)}.")

        return {
            'format': fmt,
            'size_bytes': file_size,
            'width': img.width,
            'height': img.height,
            'mode': img.mode
        }
    except Exception as e:
        raise ValueError(f"Failed to parse image headers: {str(e)}")


def validate_key_bytes(key: bytes, expected_length: int = 32) -> bool:
    """
    Validates symmetric encryption key length and type.

    Args:
        key (bytes): Key bytes to validate.
        expected_length (int): Expected key byte length (default 32 for AES-256).

    Returns:
        bool: True if key is valid bytes of expected length.

    Raises:
        ValueError: If key is not bytes or has incorrect length.
    """
    if not isinstance(key, (bytes, bytearray)):
        raise ValueError("Key must be bytes.")
    if len(key) != expected_length:
        raise ValueError(f"Key length must be exactly {expected_length} bytes (got {len(key)} bytes).")
    return True
