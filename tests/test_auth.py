import pytest
import mongomock
from unittest.mock import patch
from modules.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    create_user,
    get_user_by_username_or_email,
    get_user_by_id,
    save_user_key,
    get_user_keys,
    delete_user_key
)
import modules.database as db_module


@pytest.fixture(autouse=True)
def mock_mongo():
    with patch('modules.database.MongoClient', mongomock.MongoClient):
        db_module._client = None
        db_module._db = None
        db_module.initialize_database()
        yield
        db_module.get_db().users.delete_many({})
        db_module.get_db().key_vault.delete_many({})


def test_password_hashing():
    pwd = "SecretPassword123!"
    h = hash_password(pwd)
    assert h != pwd
    assert verify_password(pwd, h) is True
    assert verify_password("WrongPassword", h) is False


def test_jwt_token():
    token = create_access_token(user_id="507f1f77bcf86cd799439011", username="testuser", role="user")
    assert isinstance(token, str)
    payload = verify_access_token(token)
    assert payload is not None
    assert payload["sub"] == "507f1f77bcf86cd799439011"
    assert payload["username"] == "testuser"
    assert payload["role"] == "user"


def test_user_registration_and_login():
    user = create_user("alice", "alice@example.com", "Password123", role="user")
    assert isinstance(user["id"], str)
    assert user["username"] == "alice"

    # Duplicate registration error
    with pytest.raises(ValueError):
        create_user("alice", "alice2@example.com", "Password123")

    fetched = get_user_by_username_or_email("alice")
    assert fetched is not None
    assert verify_password("Password123", fetched["password_hash"]) is True

    user_by_id = get_user_by_id(user["id"])
    assert user_by_id["username"] == "alice"


def test_key_vault():
    user = create_user("bob", "bob@example.com", "Password123")
    key_id = save_user_key(user["id"], "My AES Key", "AES-256", "v9X4kL7aM2qP1oN8zR3w==")
    assert isinstance(key_id, str)

    keys = get_user_keys(user["id"])
    assert len(keys) == 1
    assert keys[0]["key_name"] == "My AES Key"

    del_res = delete_user_key(user["id"], key_id)
    assert del_res is True

    keys_after = get_user_keys(user["id"])
    assert len(keys_after) == 0
