import os
import io
import pytest
import numpy as np
import pandas as pd
from PIL import Image

from modules.encryption import generate_key, encrypt_message, decrypt_message, DecryptionError, InvalidKeyError, InvalidDataError
from modules.steganography import load_image, calculate_capacity, embed_data, extract_data, SteganographyError
from modules.feature_extraction import extract_features, extract_features_from_path
from modules.model_training import train_models, predict_image
from modules.verification import calculate_sha256, calculate_file_hash, generate_signing_keys, sign_data, verify_signature, verify_integrity
from modules.database import initialize_database, insert_record, get_records, delete_record
from modules.validation import validate_uploaded_image, validate_key_bytes


def test_validate_uploaded_image_valid():
    img = Image.new('RGB', (100, 100), color='green')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    valid_bytes = buffer.getvalue()

    meta = validate_uploaded_image(valid_bytes, filename="test.png")
    assert meta['format'] == 'PNG'
    assert meta['width'] == 100
    assert meta['height'] == 100
    assert meta['size_bytes'] == len(valid_bytes)


def test_validate_uploaded_image_empty():
    with pytest.raises(ValueError, match="empty"):
        validate_uploaded_image(b"")


def test_validate_uploaded_image_oversize():
    oversize_bytes = b"0" * (11 * 1024 * 1024)
    with pytest.raises(ValueError, match="exceeds maximum limit"):
        validate_uploaded_image(oversize_bytes)


def test_validate_uploaded_image_corrupt_content():
    corrupt_bytes = b"NOT_AN_IMAGE_HEADER_12345"
    with pytest.raises(ValueError, match="Corrupt or invalid image"):
        validate_uploaded_image(corrupt_bytes)


def test_validate_uploaded_image_invalid_extension():
    img = Image.new('RGB', (20, 20), color='blue')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    valid_bytes = buffer.getvalue()

    with pytest.raises(ValueError, match="not supported"):
        validate_uploaded_image(valid_bytes, filename="script.exe")


def test_validate_key_bytes():
    valid_key = b"0" * 32
    assert validate_key_bytes(valid_key) is True

    with pytest.raises(ValueError, match="bytes"):
        validate_key_bytes("string_key_not_bytes")

    with pytest.raises(ValueError, match="32 bytes"):
        validate_key_bytes(b"short_key")


def test_encryption_wrong_key_and_corrupt_payload():
    key1 = generate_key()
    key2 = generate_key()
    message = "StegoGuard Confidential Text"

    encrypted_b64 = encrypt_message(message, key1)

    with pytest.raises(DecryptionError):
        decrypt_message(encrypted_b64, key2)

    corrupted_b64 = encrypted_b64[:-5] + "XXXXX"
    with pytest.raises(Exception):
        decrypt_message(corrupted_b64, key1)


def test_steganography_capacity_overflow():
    img_array = np.zeros((10, 10, 3), dtype=np.uint8)
    capacity = calculate_capacity(img_array)

    oversize_payload = b"X" * (capacity + 100)

    with pytest.raises(SteganographyError, match="exceeds available capacity"):
        embed_data(img_array, oversize_payload)


def test_steganography_invalid_image_extraction():
    clean_image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    with pytest.raises(SteganographyError, match="Invalid magic identifier"):
        extract_data(clean_image)


def test_database_security_audit_rejection(tmp_path):
    db_path = str(tmp_path / "audit.db")
    initialize_database(db_path)

    with pytest.raises(ValueError, match="Security Error"):
        insert_record({'operation_type': 'Secure Encode', 'message': 'Secret Plaintext'}, db_path=db_path)

    with pytest.raises(ValueError, match="Security Error"):
        insert_record({'operation_type': 'Secure Encode', 'private_key': 'PEM KEY'}, db_path=db_path)


def test_verification_tamper_detection():
    data = b"Sensitive document content"
    priv, pub = generate_signing_keys()

    sig = sign_data(data, priv)
    assert verify_signature(data, sig, pub) is True

    tampered_data = b"Modified document content"
    assert verify_signature(tampered_data, sig, pub) is False

    corrupt_sig = bytes([b ^ 0xFF for b in sig[:5]]) + sig[5:]
    assert verify_signature(data, corrupt_sig, pub) is False


def test_end_to_end_ml_and_steganalysis(tmp_path):
    cover_arr = np.random.randint(50, 200, (60, 60, 3), dtype=np.uint8)
    key = generate_key()
    payload = encrypt_message("Hidden Message", key).encode('utf-8')
    stego_arr = embed_data(cover_arr, payload)

    cover_path = str(tmp_path / "cover.png")
    stego_path = str(tmp_path / "stego.png")

    Image.fromarray(cover_arr, 'RGB').save(cover_path)
    Image.fromarray(stego_arr, 'RGB').save(stego_path)

    feat_cover = extract_features_from_path(cover_path)
    feat_stego = extract_features_from_path(stego_path)

    assert len(feat_cover) == 29
    assert len(feat_stego) == 29

    df = pd.DataFrame([
        {**feat_cover, 'label': 0},
        {**feat_stego, 'label': 1},
        {**feat_cover, 'label': 0},
        {**feat_stego, 'label': 1},
        {**feat_cover, 'label': 0},
        {**feat_stego, 'label': 1},
        {**feat_cover, 'label': 0},
        {**feat_stego, 'label': 1}
    ])

    X = df.drop(columns=['label'])
    y = df['label']

    res = train_models(X, y, test_size=0.25, random_state=42)
    preds = predict_image(stego_path, res['models'], feature_names=res['feature_names'])

    assert len(preds) == 3
    for m, p in preds.items():
        assert 'prediction' in p
        assert 'label' in p
