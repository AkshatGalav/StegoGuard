import os
import pytest
import mongomock
from unittest.mock import patch
from modules.database import (
    initialize_database,
    insert_record,
    get_records,
    get_record_by_id,
    delete_record,
    clear_all_records
)
import modules.database as db_module


@pytest.fixture(autouse=True)
def mock_mongo():
    with patch('modules.database.MongoClient', mongomock.MongoClient):
        db_module._client = None
        db_module._db = None
        initialize_database()
        yield
        clear_all_records()


def test_insert_and_get_record():
    record_data = {
        'operation_type': 'Secure Encode',
        'input_filename': 'cover.png',
        'output_filename': 'stego.png',
        'image_hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        'payload_hash': 'a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e',
        'status': 'SUCCESS'
    }

    record_id = insert_record(record_data)
    assert isinstance(record_id, str)
    assert len(record_id) > 0

    record = get_record_by_id(record_id)
    assert record is not None
    assert record['id'] == record_id
    assert record['operation_type'] == 'Secure Encode'
    assert record['input_filename'] == 'cover.png'
    assert record['status'] == 'SUCCESS'


def test_insert_rejects_sensitive_keys():
    sensitive_records = [
        {'operation_type': 'Secure Encode', 'message': 'Secret Text Message'},
        {'operation_type': 'Secure Encode', 'plaintext': 'Sensitive Information'},
        {'operation_type': 'Secure Encode', 'key': '0123456789abcdef0123456789abcdef'},
        {'operation_type': 'Secure Encode', 'private_key': '-----BEGIN PRIVATE KEY-----'},
        {'operation_type': 'Secure Encode', 'password': 'mysecretpassword'}
    ]

    for rec in sensitive_records:
        with pytest.raises(ValueError, match="Security Error: Storing sensitive key"):
            insert_record(rec)


def test_get_records_filtering():
    rec1 = {'operation_type': 'Secure Encode', 'input_filename': 'img1.png', 'timestamp': '2026-09-01T10:00:00'}
    rec2 = {'operation_type': 'Steganalysis', 'input_filename': 'img2.png', 'timestamp': '2026-09-10T12:00:00'}
    rec3 = {'operation_type': 'Verification', 'input_filename': 'img3.png', 'timestamp': '2026-09-15T15:00:00'}

    insert_record(rec1)
    insert_record(rec2)
    insert_record(rec3)

    # Filter by operation_type
    encode_recs = get_records(operation_type='Secure Encode')
    assert len(encode_recs) == 1
    assert encode_recs[0]['input_filename'] == 'img1.png'

    steg_recs = get_records(operation_type='Steganalysis')
    assert len(steg_recs) == 1

    all_recs = get_records(operation_type='ALL')
    assert len(all_recs) == 3

    # Filter by date range
    date_filtered = get_records(start_date='2026-09-05', end_date='2026-09-12')
    assert len(date_filtered) == 1
    assert date_filtered[0]['input_filename'] == 'img2.png'


def test_delete_record():
    rec = {'operation_type': 'Secure Decode', 'input_filename': 'stego.png'}
    record_id = insert_record(rec)

    assert get_record_by_id(record_id) is not None

    deleted = delete_record(record_id)
    assert deleted is True

    assert get_record_by_id(record_id) is None
    assert delete_record(record_id) is False


def test_clear_all_records():
    insert_record({'operation_type': 'Secure Encode'})
    insert_record({'operation_type': 'Steganalysis'})

    assert len(get_records()) == 2
    assert clear_all_records() is True
    assert len(get_records()) == 0
