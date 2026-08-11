import re
import sqlite3
import os
from cryptography.fernet import Fernet
from typing import Dict, Tuple
from apexminerals.config.settings import settings

class TokenVault:
    def __init__(self):
        self.db_path = settings.DB_PATH
        self.key_path = settings.KEY_PATH
        self.fernet = self._initialize_encryption()
        self._init_db()

        # Regex patterns for sensitive Critical Mineral / Defense data
        self.patterns = {
            "SUPPLIER": r"(Supplier\s*#?[A-Z0-9-]+|Account\s*#?\d+)",
            "AMOUNT": r"(\$\d+(?:,\d{3})*(?:\.\d{2})?|\d+\s*(?:MT|Metric Tons|kg|tons))",
            "ALLOY_SPEC": r"([A-Z][a-z]?-[A-Z][a-z]?\s*alloy|NdFeB|SmCo)"
        }

    def _initialize_encryption(self) -> Fernet:
        """Loads or generates the AES-256 encryption key."""
        if not self.key_path.exists():
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as key_file:
                key_file.write(key)
        else:
            with open(self.key_path, "rb") as key_file:
                key = key_file.read()
        return Fernet(key)

    def _init_db(self):
        """Initializes the local SQLite vault for encrypted token mapping."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vault (
                    token_id TEXT PRIMARY KEY,
                    encrypted_value BLOB,
                    entity_type TEXT
                )
            """)
            conn.commit()

    def redact_and_tokenize(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Scans text, encrypts sensitive data, and replaces with surrogate tokens."""
        redacted_text = text
        token_map = {}
        token_counter = 0

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for entity_type, pattern in self.patterns.items():
                matches = re.finditer(pattern, redacted_text, re.IGNORECASE)
                for match in matches:
                    original_value = match.group(0)
                    token_id = f"[{entity_type}_{token_counter}]"
                    
                    # Encrypt and store
                    encrypted_val = self.fernet.encrypt(original_value.encode())
                    cursor.execute(
                        "INSERT OR REPLACE INTO vault (token_id, encrypted_value, entity_type) VALUES (?, ?, ?)",
                        (token_id, encrypted_val, entity_type)
                    )
                    
                    # Replace in text
                    redacted_text = redacted_text.replace(original_value, token_id)
                    token_map[token_id] = original_value
                    token_counter += 1
            conn.commit()

        return redacted_text, token_map

    def rehydrate(self, redacted_text: str) -> str:
        """Restores original sensitive values from tokens before showing to user."""
        rehydrated_text = redacted_text
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT token_id, encrypted_value FROM vault")
            rows = cursor.fetchall()
            
            for token_id, encrypted_val in rows:
                if token_id in rehydrated_text:
                    decrypted_val = self.fernet.decrypt(encrypted_val).decode()
                    rehydrated_text = rehydrated_text.replace(token_id, decrypted_val)
                    
        return rehydrated_text