from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from database import get_db, get_redis
from models import User, TokenType, UserRole
from utils.jwt_handler import decode_token
import redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/aurora_api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    token_data = decode_token(token, TokenType.ACCESS)
    if token_data is None:
        raise credentials_exception
    
    # Check if token is blacklisted
    jti = get_token_jti(token, TokenType.ACCESS)
    if jti and redis_client.get(f"blacklist:{jti}"):
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def require_role(allowed_roles: list[UserRole]):
    """Dependency factory for role-based access control"""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker