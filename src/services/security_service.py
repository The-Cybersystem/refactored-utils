from cryptography.fernet import Fernet
from src.utils.config import ConfigManager, ConfigurationError
import logging
import base64
import hashlib


class SecurityService:
    def __init__(self):
        self.config = ConfigManager()
        logging.info("Initialising security service...")
        self._initialise_encryption()

    def _initialise_encryption(self):
        """Initializes the Fernet cipher using a hashed secret from config."""
        secret = self.config.get("ENCRYPTION_SECRET")
        if not secret:
            raise ConfigurationError("Encryption secret not found in configuration.")

        # Derive a 32-byte key from the secret
        key = hashlib.sha256(secret.encode()).digest()
        self.cipher = Fernet(base64.urlsafe_b64encode(key))
        logging.info("Security service initialised successfully.")

    def encrypt(self, data: str) -> str:
        """
        Encrypts a string using the initialized cipher.

        Args:
            data: The plaintext string to encrypt.

        Returns:
            str: The encrypted string.
        """
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        """
        Decrypts a string using the initialized cipher.

        Args:
            data: The encrypted string to decrypt.

        Returns:
            str: The decrypted plaintext string.
        """
        return self.cipher.decrypt(data.encode()).decode()
