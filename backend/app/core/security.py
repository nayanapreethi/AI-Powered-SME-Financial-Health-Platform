"""
SME-Pulse AI - Security Utilities
AES-256 encryption, JWT authentication, and password hashing
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Security manager for encryption and decryption"""
    
    def __init__(self):
        self._encryption_key = settings.ENCRYPTION_KEY.encode()
        self._fernet = None
        self._setup_fernet()
    
    def _setup_fernet(self):
        """Setup Fernet instance for symmetric encryption"""
        try:
            # Generate a proper 32-byte key from the encryption key
            key_bytes = hashlib.sha256(self._encryption_key).digest()
            self._fernet = Fernet(key_bytes)
        except Exception as e:
            logger.error(f"Failed to setup encryption: {e}")
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt sensitive data using AES-256"""
        if not plaintext:
            return ""
        try:
            encrypted = self._fernet.encrypt(plaintext.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt sensitive data"""
        if not ciphertext:
            return ""
        try:
            decoded = base64.b64decode(ciphertext.encode())
            decrypted = self._fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)


# Global security manager instance
security_manager = SecurityManager()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT decode failed: {e}")
        return None


def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"sk_{secrets.token_hex(32)}"


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data for display (e.g., account numbers)"""
    if not data or len(data) <= visible_chars:
        return data
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]

