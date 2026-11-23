import unittest
import os
import tempfile
import base64
import json
from Crypto.Random import get_random_bytes

from modules.encryption import (
    generate_key,
    save_key_securely,
    load_key_securely,
    encrypt_message,
    decrypt_message,
    InvalidKeyError,
    DecryptionError,
    InvalidDataError
)

class TestEncryptionModule(unittest.TestCase):
    
    def setUp(self):
        self.message = "This is a highly confidential secret message."
        self.key = generate_key()
        
    def test_key_generation(self):
        key1 = generate_key()
        key2 = generate_key()
        self.assertEqual(len(key1), 32)
        self.assertEqual(len(key2), 32)
        self.assertNotEqual(key1, key2)
        
    def test_save_and_load_key(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            path = tmp.name
            
        try:
            save_key_securely(self.key, path)
            loaded_key = load_key_securely(path)
            self.assertEqual(self.key, loaded_key)
        finally:
            if os.path.exists(path):
                os.remove(path)
                
    def test_encryption_decryption_success(self):
        encrypted = encrypt_message(self.message, self.key)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(self.message, encrypted)
        
        decrypted = decrypt_message(encrypted, self.key)
        self.assertEqual(self.message, decrypted)
        
    def test_wrong_key_failure(self):
        encrypted = encrypt_message(self.message, self.key)
        wrong_key = generate_key()
        
        with self.assertRaises(DecryptionError):
            decrypt_message(encrypted, wrong_key)
            
    def test_invalid_key_length(self):
        invalid_key = get_random_bytes(16) # Only 128 bits
        with self.assertRaises(InvalidKeyError):
            encrypt_message(self.message, invalid_key)
            
        with self.assertRaises(InvalidKeyError):
            decrypt_message("dummy_data", invalid_key)
            
    def test_modified_ciphertext_failure(self):
        encrypted = encrypt_message(self.message, self.key)
        
        # Modify the ciphertext
        json_data = base64.b64decode(encrypted).decode('utf-8')
        payload = json.loads(json_data)
        
        # Flip a bit in ciphertext
        ct_bytes = bytearray(base64.b64decode(payload['ciphertext']))
        ct_bytes[0] ^= 1 
        payload['ciphertext'] = base64.b64encode(ct_bytes).decode('utf-8')
        
        modified_encrypted = base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')
        
        with self.assertRaises(DecryptionError):
            decrypt_message(modified_encrypted, self.key)
            
    def test_empty_message(self):
        with self.assertRaises(ValueError):
            encrypt_message("", self.key)
            
    def test_empty_encrypted_data(self):
        with self.assertRaises(ValueError):
            decrypt_message("", self.key)

if __name__ == '__main__':
    unittest.main()
