from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.utils.logging_system import log_errors, system_logger
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@log_errors(system_logger)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@log_errors(system_logger)
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@log_errors(system_logger)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


@log_errors(system_logger)
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a refresh token with longer expiration"""
    to_encode = data.copy()
    # Default refresh token expiration: 7 days
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


@log_errors(system_logger)
def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        token_type_value: str = payload.get("type")
        
        if username is None:
            return None
        
        # Verify token type if specified
        if token_type and token_type_value != token_type:
            return None
        
        return username
    except JWTError:
        return None


@log_errors(system_logger)
def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


@log_errors(system_logger)
def generate_refresh_token_id() -> str:
    return secrets.token_urlsafe(32)