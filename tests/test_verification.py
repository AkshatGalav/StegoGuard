import os
import pytest
import hashlib
from modules.verification import (
    calculate_sha256,
    calculate_file_hash,
    generate_signing_keys,
    sign_data,
    verify_signature,
    verify_integrity
)


def test_calculate_sha256_bytes_and_str():
    msg_str = "StegoGuard Integrity Test Payload"
    msg_bytes = msg_str.encode('utf-8')
    expected = hashlib.sha256(msg_bytes).hexdigest()

    assert calculate_sha256(msg_str) == expected
    assert calculate_sha256(msg_bytes) == expected


def test_calculate_sha256_invalid():
    with pytest.raises(ValueError):
        calculate_sha256(None)
    with pytest.raises(ValueError):
        calculate_sha256(12345)


def test_calculate_file_hash(tmp_path):
    file_path = tmp_path / "sample_file.bin"
    sample_content = b"Binary file contents for SHA256 test"
    file_path.write_bytes(sample_content)

    expected = hashlib.sha256(sample_content).hexdigest()
    assert calculate_file_hash(str(file_path)) == expected


def test_calculate_file_hash_missing():
    with pytest.raises(FileNotFoundError):
        calculate_file_hash("non_existent_file_99999.txt")


def test_verify_integrity_valid_and_modified():
    data = b"Authentic payload data"
    data_hash = calculate_sha256(data)

    assert verify_integrity(data, data_hash) is True
    assert verify_integrity(data, data_hash.upper()) is True

    modified_data = b"Modified payload data"
    assert verify_integrity(modified_data, data_hash) is False
    assert verify_integrity(data, "0000000000000000000000000000000000000000000000000000000000000000") is False


def test_rsa_key_generation():
    private_pem, public_pem = generate_signing_keys(2048)
    assert b"BEGIN PRIVATE KEY" in private_pem
    assert b"BEGIN PUBLIC KEY" in public_pem


def test_valid_digital_signature():
    private_pem, public_pem = generate_signing_keys()
    payload = b"Payload message to sign digitally"

    signature = sign_data(payload, private_pem)
    assert isinstance(signature, bytes)
    assert len(signature) > 0

    is_valid = verify_signature(payload, signature, public_pem)
    assert is_valid is True


def test_tampered_payload_signature_failure():
    private_pem, public_pem = generate_signing_keys()
    original_payload = b"Original payload message"
    tampered_payload = b"Tampered payload message"

    signature = sign_data(original_payload, private_pem)
    assert verify_signature(tampered_payload, signature, public_pem) is False


def test_tampered_signature_bytes_failure():
    private_pem, public_pem = generate_signing_keys()
    payload = b"Payload message to sign digitally"

    signature = sign_data(payload, private_pem)
    corrupted_signature = bytes([b ^ 0xFF for b in signature[:10]]) + signature[10:]

    assert verify_signature(payload, corrupted_signature, public_pem) is False


def test_wrong_public_key_signature_failure():
    private_pem_1, public_pem_1 = generate_signing_keys()
    private_pem_2, public_pem_2 = generate_signing_keys()
    payload = b"Payload message signed by Key 1"

    signature = sign_data(payload, private_pem_1)

    # Verification using public key 2 must fail
    assert verify_signature(payload, signature, public_pem_2) is False
