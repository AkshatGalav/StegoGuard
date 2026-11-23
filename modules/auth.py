"""
Authentication & User Profile Module.
Provides password hashing (Bcrypt), JWT authentication token management,
user registration/login CRUD, and Cryptographic Key Vault database operations using MongoDB.
"""

import os
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict
from bson.objectid import ObjectId

from modules.database import get_db, initialize_database, _convert_id

JWT_SECRET_KEY = os.getenv("STEGOGUARD_JWT_SECRET", "stegoguard-secret-quantum-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def hash_password(password: str) -> str:
    """Hashes a plaintext password using Bcrypt with random salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verifies a plaintext password against a stored Bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def create_access_token(user_id: str, username: str, role: str = "user") -> str:
    """Generates a signed JWT access token containing user identity claims."""
    now = datetime.now(timezone.utc)
    expiration = now + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": now,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT token. Returns token payload dict or None."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None


# USER DATABASE CRUD OPERATIONS

def create_user(username: str, email: str, password: str, role: str = "user", db_path=None) -> dict:
    """Registers a new user in the MongoDB database."""
    initialize_database(db_path)
    username = username.strip().lower()
    email = email.strip().lower()

    if not username or not email or not password:
        raise ValueError("Username, email, and password are required.")

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    db = get_db()
    
    # Check for existing user
    if db.users.find_one({"$or": [{"username": username}, {"email": email}]}):
        raise ValueError("Username or email already exists.")

    pwd_hash = hash_password(password)
    now_iso = datetime.now(timezone.utc).isoformat()

    user_doc = {
        "username": username,
        "email": email,
        "password_hash": pwd_hash,
        "role": role,
        "created_at": now_iso
    }
    
    result = db.users.insert_one(user_doc)
    
    return {
        "id": str(result.inserted_id),
        "username": username,
        "email": email,
        "role": role,
        "created_at": now_iso
    }


def get_user_by_username_or_email(identifier: str, db_path=None) -> Optional[dict]:
    """Retrieves user record by username or email."""
    identifier = identifier.strip().lower()
    db = get_db()
    user = db.users.find_one({"$or": [{"username": identifier}, {"email": identifier}]})
    return _convert_id(user)


def get_user_by_id(user_id: str, db_path=None) -> Optional[dict]:
    """Retrieves user profile dict by ID."""
    db = get_db()
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        return _convert_id(user)
    except Exception:
        return None


# CRYPTOGRAPHIC KEY VAULT CRUD

def save_user_key(user_id: str, key_name: str, key_type: str, key_data: str, db_path=None) -> str:
    """Saves a cryptographic key or RSA keypair into user's private key vault."""
    initialize_database(db_path)
    now_iso = datetime.now(timezone.utc).isoformat()
    db = get_db()

    key_doc = {
        "user_id": str(user_id),
        "key_name": key_name,
        "key_type": key_type,
        "key_data": key_data,
        "created_at": now_iso
    }
    
    result = db.key_vault.insert_one(key_doc)
    return str(result.inserted_id)


def get_user_keys(user_id: str, db_path=None) -> list[dict]:
    """Retrieves all keys in a user's private vault."""
    db = get_db()
    cursor = db.key_vault.find({"user_id": str(user_id)}).sort("_id", -1)
    return [_convert_id(doc) for doc in cursor]


def delete_user_key(user_id: str, key_id: str, db_path=None) -> bool:
    """Deletes a key from a user's vault by key ID."""
    db = get_db()
    try:
        result = db.key_vault.delete_one({"_id": ObjectId(key_id), "user_id": str(user_id)})
        return result.deleted_count > 0
    except Exception:
        return False
