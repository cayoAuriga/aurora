from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from config import settings
from models import TokenType, TokenData
import uuid

def create_access_token(data: Dict[str, Any]) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({
        "exp": expire,
        "type": TokenType.ACCESS,
        "jti": str(uuid.uuid4())  # JWT ID for token blacklisting
    })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({
        "exp": expire,
        "type": TokenType.REFRESH,
        "jti": str(uuid.uuid4())
    })
    return jwt.encode(to_encode, settings.refresh_secret_key, algorithm=settings.algorithm)

def decode_token(token: str, token_type: TokenType = TokenType.ACCESS) -> Optional[TokenData]:
    """Decode and validate JWT token"""
    try:
        secret = settings.secret_key if token_type == TokenType.ACCESS else settings.refresh_secret_key
        payload = jwt.decode(token, secret, algorithms=[settings.algorithm])
        
        # Validate token type
        if payload.get("type") != token_type:
            return None
            
        return TokenData(
            user_id=payload.get("sub"),
            username=payload.get("username"),
            email=payload.get("email"),
            role=payload.get("role"),
            token_type=token_type
        )
    except JWTError:
        return None

def get_token_jti(token: str, token_type: TokenType = TokenType.ACCESS) -> Optional[str]:
    """Extract JTI (JWT ID) from token"""
    try:
        secret = settings.secret_key if token_type == TokenType.ACCESS else settings.refresh_secret_key
        payload = jwt.decode(token, secret, algorithms=[settings.algorithm])
        return payload.get("jti")
    except JWTError:
        return None