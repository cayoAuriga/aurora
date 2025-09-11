from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum as SQLEnum, Integer, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

# SQLAlchemy Models
class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"
    
    id = Column(String(36), primary_key=True)
    token = Column(String(255), unique=True, nullable=False)  # SHA256 hash
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(String(36), primary_key=True)
    token = Column(String(255), unique=True, nullable=False)  # SHA256 hash
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
 
class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)  # UUID
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Deprecated, usar email_verified
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    
    # Security fields
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_failed_login = Column(DateTime, nullable=True)
    
    # 2FA fields
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)  # Encrypted in production
    two_factor_backup_codes = Column(Text, nullable=True)  # Comma-separated hashes
    
    # Account deletion fields
    deletion_requested_at = Column(DateTime, nullable=True)
    deletion_scheduled_for = Column(DateTime, nullable=True)
    deletion_reason = Column(Text, nullable=True)
    
    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    email_verification_tokens = relationship("EmailVerificationToken", back_populates="user")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")

# Actualizar RefreshToken para incluir campos faltantes
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(String(36), primary_key=True)
    token = Column(Text, unique=True, nullable=False)  # SHA256 hash
    jti = Column(String(255), unique=True, nullable=False, index=True)  # JWT ID
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="refresh_tokens")

# Establecer las relaciones en los otros modelos
EmailVerificationToken.user = relationship("User", back_populates="email_verification_tokens")
PasswordResetToken.user = relationship("User", back_populates="password_reset_tokens")

# Pydantic Models
# Pydantic Models adicionales que faltan

class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str  # Can be username or email
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    token_type: TokenType

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

class ResetPasswordRequest(BaseModel):
 token: str
new_password: str = Field(..., min_length=8, max_length=100)
    
@validator('new_password')
def validate_password(cls, v):
    if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
    if not any(char.isdigit() for char in v):
        raise ValueError('Password must contain at least one digit')
    if not any(char.isupper() for char in v):
        raise ValueError('Password must contain at least one uppercase letter')
    if not any(char.islower() for char in v):
        raise ValueError('Password must contain at least one lowercase letter')
    return v


class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
# Modelos adicionales para respuestas
class MessageResponse(BaseModel):
    message: str

class SessionResponse(BaseModel):
    id: str
    created_at: datetime
    last_used: Optional[datetime]
    ip_address: Optional[str]
    user_agent: Optional[str]
    expires_at: datetime

class SessionsListResponse(BaseModel):
    active_sessions: List[SessionResponse]

class TwoFactorSetupResponse(BaseModel):
    secret: str
    qr_code: str
    manual_entry: str

class TwoFactorBackupCodesResponse(BaseModel):
    message: str
    backup_codes: List[str]

class UsernameCheckResponse(BaseModel):
    available: bool
    message: str

class EmailCheckResponse(BaseModel):
    available: bool
    message: str

class AccountDeletionResponse(BaseModel):
    message: str
    scheduled_for: datetime
    note: str

class TokenVerificationResponse(BaseModel):
    valid: bool
    user_id: str
    username: str
    email: str
    role: str
    is_active: bool
    email_verified: bool