"""
Database Module.

Manages MongoDB data persistence for audit logs and evidence history in StegoGuard.
Ensures strict privacy: plaintext secret messages, encryption keys, passwords, and 
private keys are NEVER logged or stored.
"""

import os
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timezone

FORBIDDEN_SENSITIVE_KEYS = {
    'message', 'plaintext', 'secret', 'key', 'private_key', 'password', 'passphrase', 'decrypted_message'
}

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is not None:
        return _db
    
    uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
    _client = MongoClient(uri)
    _db = _client.get_database("stegoguard")
    return _db

def initialize_database(db_path=None):
    """
    Creates indexes for the collections if they do not exist.
    """
    db = get_db()
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True)
    db.key_vault.create_index("user_id")
    db.evidence_history.create_index("user_id")


def _convert_id(doc):
    if doc and '_id' in doc:
        doc['id'] = str(doc.pop('_id'))
    return doc


def insert_record(record_data: dict, db_path=None):
    """
    Inserts an operational audit record into the evidence_history collection.

    Args:
        record_data (dict): Dictionary containing record fields.
        db_path: Ignored, kept for backward compatibility with tests.

    Returns:
        str: The string representation of the inserted ObjectId.
    """
    # Strict privacy audit
    for k in record_data:
        if k.lower() in FORBIDDEN_SENSITIVE_KEYS and record_data[k]:
            raise ValueError(f"Security Error: Storing sensitive key '{k}' in evidence history is strictly forbidden.")

    operation_type = record_data.get('operation_type')
    if not operation_type:
        raise ValueError("Record data must specify 'operation_type'.")

    if 'timestamp' not in record_data:
        record_data['timestamp'] = datetime.now(timezone.utc).isoformat()

    if 'status' not in record_data:
        record_data['status'] = 'SUCCESS'

    db = get_db()
    result = db.evidence_history.insert_one(record_data)
    return str(result.inserted_id)


def get_records(
    user_id = None,
    operation_type: str = None,
    start_date: str = None,
    end_date: str = None,
    db_path = None
) -> list[dict]:
    """
    Retrieves evidence history records with optional filtering.
    """
    db = get_db()
    query = {}

    if user_id is not None:
        query["user_id"] = user_id

    if operation_type and operation_type.upper() != "ALL":
        query["operation_type"] = operation_type

    if start_date or end_date:
        timestamp_query = {}
        if start_date:
            timestamp_query["$gte"] = f"{start_date}T00:00:00"
        if end_date:
            timestamp_query["$lte"] = f"{end_date}T23:59:59"
        query["timestamp"] = timestamp_query

    cursor = db.evidence_history.find(query).sort("timestamp", pymongo.DESCENDING)
    return [_convert_id(doc) for doc in cursor]


def get_record_by_id(record_id, db_path=None) -> dict | None:
    """
    Retrieves a single record by string ID.
    """
    db = get_db()
    try:
        doc = db.evidence_history.find_one({"_id": ObjectId(record_id)})
        return _convert_id(doc)
    except Exception:
        return None


def delete_record(record_id, db_path=None) -> bool:
    """
    Deletes an evidence history record by string ID.
    """
    db = get_db()
    try:
        result = db.evidence_history.delete_one({"_id": ObjectId(record_id)})
        return result.deleted_count > 0
    except Exception:
        return False


def clear_all_records(db_path=None) -> bool:
    """
    Clears all records from evidence history.
    """
    db = get_db()
    try:
        db.evidence_history.delete_many({})
        return True
    except Exception:
        return False
