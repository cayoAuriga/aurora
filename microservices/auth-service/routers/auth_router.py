# from fastapi import APIRouter, Depends, HTTPException, status, Response, Header, Request
# from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, update, delete, or_, and_, func
# from datetime import datetime, timedelta
# from typing import Optional, Dict
# import uuid
# import secrets
# import hashlib
# import asyncio
# from database import get_db_connection
# from models import (
#     User, UserCreate,  UserResponse, UserRole,
#     RefreshToken,
#     EmailVerificationToken, PasswordResetToken, TokenType
# )
# from utils.password import hash_password, verify_password
# from utils.jwt_handler import (
#     create_access_token, create_refresh_token, 
#     decode_token, get_token_jti
# )
# from utils.email import send_verification_email, send_password_reset_email
# # from dependencies import get_current_user, oauth2_scheme

# import redis.asyncio as redis
# from sqlalchemy import Index

# # Agregar después de las definiciones de las clases
# Index('idx_email_verification_user', EmailVerificationToken.user_id, EmailVerificationToken.used)
# Index('idx_password_reset_user', PasswordResetToken.user_id, PasswordResetToken.used)
# Index('idx_refresh_token_user', RefreshToken.user_id, RefreshToken.revoked)
from fastapi import APIRouter, Depends, HTTPException, status, Request

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

# Rate limiting helper
# async def check_rate_limit(
#     redis_client: redis.Redis,
#     key: str,
#     max_attempts: int,
#     window_seconds: int
# ) -> bool:
#     """Check if rate limit is exceeded"""
#     current = await redis_client.incr(key)
#     if current == 1:
#         await redis_client.expire(key, window_seconds)
#     return current <= max_attempts

# # Token blacklist check
# async def is_token_blacklisted(
#     token: str,
#     redis_client: redis.Redis
# ) -> bool:
#     """Check if token is blacklisted"""
#     jti = get_token_jti(token, TokenType.ACCESS)
#     if jti:
#         exists = await redis_client.exists(f"blacklist:{jti}")
#         return bool(exists)
#     return False

@router.post("/register")
async def register(
    # user_data: UserCreate,
    # request: Request,
    # db: AsyncSession = Depends(get_db_connection),
    # redis_client: redis.Redis = Depends(get_redis)
):
    """
    Register a new user
    
    - Email verification required
    - Username must be unique
    - Password must meet complexity requirements
    """
    # # Rate limiting (5 registrations per IP per hour)
    # client_ip = request.client.host
    # if not await check_rate_limit(
    #     # redis_client, 
    #     f"register:{client_ip}", 
    #     max_attempts=5, 
    #     window_seconds=3600
    # ):
    #     raise HTTPException(
    #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    #         detail="Too many registration attempts. Please try again later."
    #     )
    
    # # Check if user exists
    # result = await db.execute(
    #     select(User).where(
    #         or_(
    #             User.email == user_data.email.lower(),
    #             User.username == user_data.username.lower()
    #         )
    #     )
    # )
    # existing_user = result.scalar_one_or_none()
    
    # if existing_user:
    #     if existing_user.email == user_data.email.lower():
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Email already registered"
    #         )
    #     else:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Username already taken"
    #         )
    
    # # Create new user
    # new_user = User(
    #     id=str(uuid.uuid4()),
    #     email=user_data.email.lower(),
    #     username=user_data.username.lower(),
    #     full_name=user_data.full_name,
    #     hashed_password=hash_password(user_data.password),
    #     role=user_data.role or UserRole.USER,
    #     is_active=False,  # Requires email verification
    #     email_verified=False,
    #     failed_login_attempts=0,
    #     created_at=datetime.utcnow()
    # )
    
    # db.add(new_user)
    
    # # Create email verification token
    # verification_token = secrets.token_urlsafe(32)
    # email_token = EmailVerificationToken(
    #     id=str(uuid.uuid4()),
    #     token=hashlib.sha256(verification_token.encode()).hexdigest(),
    #     user_id=new_user.id,
    #     expires_at=datetime.utcnow() + timedelta(hours=24),
    #     used=False
    # )
    # db.add(email_token)
    
    # await db.commit()
    # await db.refresh(new_user)
    
    # # Send verification email (async)
    # asyncio.create_task(send_verification_email(new_user.email, verification_token))
    
    # return new_user
    return {"message": "Registration endpoint is under maintenance."}

# @router.post("/verify-email")
# async def verify_email(
#     token: str,
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """Verify email address with token"""
#     # Hash the token to compare with stored hash
#     token_hash = hashlib.sha256(token.encode()).hexdigest()
    
#     # Find token
#     result = await db.execute(
#         select(EmailVerificationToken).where(
#             EmailVerificationToken.token == token_hash,
#             EmailVerificationToken.used == False,
#             EmailVerificationToken.expires_at > datetime.utcnow()
#         )
#     )
#     email_token = result.scalar_one_or_none()
    
#     if not email_token:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired verification token"
#         )
    
#     # Activate user
#     result = await db.execute(
#         select(User).where(User.id == email_token.user_id)
#     )
#     user = result.scalar_one_or_none()
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
    
#     user.is_active = True
#     user.email_verified = True
#     user.email_verified_at = datetime.utcnow()
    
#     # Mark token as used
#     email_token.used = True
#     email_token.used_at = datetime.utcnow()
    
#     await db.commit()
    
#     return {"message": "Email verified successfully. You can now login."}

# @router.post("/login", response_model=Token)
# async def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     request: Request = None,
#     db: AsyncSession = Depends(get_db_connection),
#     redis_client: redis.Redis = Depends(get_redis)
# ):
#     """
#     Login with username/email and password
    
#     - Returns access and refresh tokens
#     - Tracks failed login attempts
#     - Implements account lockout after 5 failed attempts
#     """
#     client_ip = request.client.host if request else "unknown"
    
#     # Rate limiting (10 login attempts per IP per minute)
#     if not await check_rate_limit(
#         redis_client,
#         f"login:{client_ip}",
#         max_attempts=10,
#         window_seconds=60
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#             detail="Too many login attempts. Please try again later."
#         )
    
#     # Find user by username or email
#     username_lower = form_data.username.lower()
#     result = await db.execute(
#         select(User).where(
#             or_(
#                 User.username == username_lower,
#                 User.email == username_lower
#             )
#         )
#     )
#     user = result.scalar_one_or_none()
    
#     if not user:
#         # Sleep to prevent timing attacks
#         await asyncio.sleep(0.5)
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # Check if account is locked
#     if user.locked_until and user.locked_until > datetime.utcnow():
#         remaining = (user.locked_until - datetime.utcnow()).total_seconds()
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=f"Account locked. Try again in {int(remaining/60)} minutes."
#         )
    
#     # Verify password
#     if not verify_password(form_data.password, user.hashed_password):
#         # Track failed login attempts
#         user.failed_login_attempts += 1
#         user.last_failed_login = datetime.utcnow()
        
#         if user.failed_login_attempts >= 5:
#             user.locked_until = datetime.utcnow() + timedelta(minutes=30)
#             await db.commit()
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Account locked due to multiple failed login attempts"
#             )
        
#         await db.commit()
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # Check if email is verified (skip for admin users)
#     if not user.email_verified and user.role != UserRole.ADMIN:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Please verify your email before logging in"
#         )
    
#     # Check if user is active
#     if not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Account has been deactivated"
#         )
    
#     # Reset failed login attempts
#     user.failed_login_attempts = 0
#     user.locked_until = None
#     user.last_login = datetime.utcnow()
#     user.last_login_ip = client_ip
#     await db.commit()
    
#     # Create tokens
#     token_data = {
#         "sub": user.id,
#         "username": user.username,
#         "email": user.email,
#         "role": user.role.value if hasattr(user.role, 'value') else user.role
#     }
    
#     access_token = create_access_token(token_data)
#     refresh_token = create_refresh_token(token_data)
    
#     # Get JTI from refresh token for storage
#     refresh_jti = get_token_jti(refresh_token, TokenType.REFRESH)
    
#     # Store refresh token in database
#     refresh_token_db = RefreshToken(
#         id=str(uuid.uuid4()),
#         token=hashlib.sha256(refresh_token.encode()).hexdigest(),
#         jti=refresh_jti,
#         user_id=user.id,
#         expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
#         created_at=datetime.utcnow(),
#         ip_address=client_ip,
#         user_agent=request.headers.get("User-Agent", "unknown") if request else "unknown",
#         revoked=False
#     )
#     db.add(refresh_token_db)
#     await db.commit()
    
#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer"
#     }

# @router.post("/refresh", response_model=Token)
# async def refresh_token(
#     request_data: RefreshTokenRequest,
#     request: Request = None,
#     db: AsyncSession = Depends(get_db_connection),
#     redis_client: redis.Redis = Depends(get_redis)
# ):
#     """
#     Refresh access token using refresh token
    
#     - Validates refresh token
#     - Issues new access and refresh tokens
#     - Revokes old refresh token
#     """
#     # Decode refresh token
#     token_data = decode_token(request_data.refresh_token, TokenType.REFRESH)
#     if not token_data:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token"
#         )
    
#     # Get JTI from refresh token
#     refresh_jti = get_token_jti(request_data.refresh_token, TokenType.REFRESH)
    
#     # Check if refresh token exists and is valid
#     token_hash = hashlib.sha256(request_data.refresh_token.encode()).hexdigest()
#     result = await db.execute(
#         select(RefreshToken).where(
#             RefreshToken.token == token_hash,
#             RefreshToken.revoked == False,
#             RefreshToken.expires_at > datetime.utcnow()
#         )
#     )
#     stored_token = result.scalar_one_or_none()
    
#     if not stored_token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired refresh token"
#         )
    
#     # Get user
#     result = await db.execute(
#         select(User).where(User.id == token_data.user_id)
#     )
#     user = result.scalar_one_or_none()

#     if not user or not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found or inactive"
#         )

#     # Create new tokens
#     new_token_data = {
#         "sub": user.id,
#         "username": user.username,
#         "email": user.email,
#         "role": user.role.value if hasattr(user.role, 'value') else user.role
#     }

#     new_access_token = create_access_token(new_token_data)
#     new_refresh_token = create_refresh_token(new_token_data)

#     # Get JTI from new refresh token
#     new_refresh_jti = get_token_jti(new_refresh_token, TokenType.REFRESH)

#     # Revoke old refresh token
#     stored_token.revoked = True
#     stored_token.revoked_at = datetime.utcnow()

#     # Store new refresh token
#     client_ip = request.client.host if request else "unknown"
#     new_refresh_token_db = RefreshToken(
#         id=str(uuid.uuid4()),
#         token=hashlib.sha256(new_refresh_token.encode()).hexdigest(),
#         jti=new_refresh_jti,
#         user_id=user.id,
#         expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
#         created_at=datetime.utcnow(),
#         ip_address=client_ip,
#         user_agent=request.headers.get(
#             "User-Agent", "unknown") if request else "unknown",
#         revoked=False
#     )
#     db.add(new_refresh_token_db)
#     await db.commit()

#     return {
#         "access_token": new_access_token,
#         "refresh_token": new_refresh_token,
#         "token_type": "bearer"
#     }


# @router.post("/logout")
# async def logout(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db_connection),
#     redis_client: redis.Redis = Depends(get_redis),
#     token: str = Depends(oauth2_scheme)
# ):
#     """
#     Logout user and blacklist token

#     - Blacklists current access token
#     - Revokes all user's refresh tokens
#     """
#     # Get token JTI and add to blacklist
#     jti = get_token_jti(token, TokenType.ACCESS)
#     if jti:
#         # Add to blacklist with expiration
#         await redis_client.setex(
#             f"blacklist:{jti}",
#             settings.access_token_expire_minutes * 60,
#             "1"
#         )

#     # Revoke all user's refresh tokens
#     stmt = (
#         update(RefreshToken)
#         .where(
#             RefreshToken.user_id == current_user.id,
#             RefreshToken.revoked == False
#         )
#         .values(
#             revoked=True,
#             revoked_at=datetime.utcnow()
#         )
#     )
#     await db.execute(stmt)
#     await db.commit()

#     return {"message": "Successfully logged out"}


# @router.post("/logout-all")
# async def logout_all_devices(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db_connection),
#     redis_client: redis.Redis = Depends(get_redis),
#     token: str = Depends(oauth2_scheme)
# ):
#     """
#     Logout from all devices

#     - Revokes all user's refresh tokens
#     - Invalidates all sessions
#     """
#     # Blacklist current token
#     jti = get_token_jti(token, TokenType.ACCESS)
#     if jti:
#         await redis_client.setex(
#             f"blacklist:{jti}",
#             settings.access_token_expire_minutes * 60,
#             "1"
#         )

#     # Revoke ALL user's refresh tokens
#     stmt = (
#         update(RefreshToken)
#         .where(RefreshToken.user_id == current_user.id)
#         .values(
#             revoked=True,
#             revoked_at=datetime.utcnow()
#         )
#     )
#     await db.execute(stmt)

#     # Add user to force-logout list (all tokens before this timestamp are invalid)
#     await redis_client.setex(
#         f"force_logout:{current_user.id}",
#         86400,  # 24 hours
#         str(datetime.utcnow().timestamp())
#     )

#     await db.commit()

#     return {"message": "Successfully logged out from all devices"}


# @router.post("/change-password")
# async def change_password(
#     password_data: ChangePassword,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db_connection),
#     redis_client: redis.Redis = Depends(get_redis)
# ):
#     """
#     Change user password

#     - Verifies current password
#     - Updates to new password
#     - Revokes all refresh tokens (forces re-login)
#     """
#     # Verify current password
#     if not verify_password(password_data.current_password, current_user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Incorrect current password"
#         )

#     # Check if new password is same as current
#     if verify_password(password_data.new_password, current_user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="New password must be different from current password"
#         )

#     # Update password
#     current_user.hashed_password = hash_password(password_data.new_password)
#     current_user.password_changed_at = datetime.utcnow()

#     # Revoke all refresh tokens (force re-login)
#     stmt = (
#         update(RefreshToken)
#         .where(
#             RefreshToken.user_id == current_user.id,
#             RefreshToken.revoked == False
#         )
#         .values(
#             revoked=True,
#             revoked_at=datetime.utcnow()
#         )
#     )
#     await db.execute(stmt)

#     await db.commit()

#     return {"message": "Password changed successfully. Please login again."}


# @router.post("/forgot-password")
# async def forgot_password(
#     request_data: ResetPasswordRequest,
#     request: Request,
#     db: AsyncSession = Depends(get_db_connection),
#     redis_client: redis.Redis = Depends(get_redis)
# ):
#     """
#     Request password reset

#     - Sends reset email with token
#     - Token valid for 1 hour
#     """
#     client_ip = request.client.host

#     # Rate limiting (3 requests per email per hour)
#     if not await check_rate_limit(
#         redis_client,
#         f"forgot_password:{request_data.email}",
#         max_attempts=3,
#         window_seconds=3600
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#             detail="Too many password reset requests. Please try again later."
#         )

#     # Find user by email
#     result = await db.execute(
#         select(User).where(User.email == request_data.email.lower())
#     )
#     user = result.scalar_one_or_none()

#     # Always return success (don't reveal if email exists)
#     if not user:
#         await asyncio.sleep(0.5)  # Simulate processing time
#         return {
#             "message": "If the email exists, a password reset link has been sent."
#         }

#     # Invalidate any existing reset tokens
#     stmt = (
#         update(PasswordResetToken)
#         .where(
#             PasswordResetToken.user_id == user.id,
#             PasswordResetToken.used == False
#         )
#         .values(
#             used=True,
#             used_at=datetime.utcnow()
#         )
#     )
#     await db.execute(stmt)

#     # Create reset token
#     reset_token = secrets.token_urlsafe(32)
#     reset_token_db = PasswordResetToken(
#         id=str(uuid.uuid4()),
#         token=hashlib.sha256(reset_token.encode()).hexdigest(),
#         user_id=user.id,
#         expires_at=datetime.utcnow() + timedelta(hours=1),
#         created_at=datetime.utcnow(),
#         ip_address=client_ip,
#         used=False
#     )
#     db.add(reset_token_db)
#     await db.commit()

#     # Send reset email (async)
#     asyncio.create_task(send_password_reset_email(user.email, reset_token))

#     return {
#         "message": "If the email exists, a password reset link has been sent."
#     }


# @router.post("/reset-password")
# async def reset_password(
#     reset_data: ResetPasswordConfirm,
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """
#     Reset password with token

#     - Validates reset token
#     - Updates password
#     - Revokes all refresh tokens
#     """
#     # Hash token to compare
#     token_hash = hashlib.sha256(reset_data.token.encode()).hexdigest()

#     # Find valid token
#     result = await db.execute(
#         select(PasswordResetToken).where(
#             PasswordResetToken.token == token_hash,
#             PasswordResetToken.used == False,
#             PasswordResetToken.expires_at > datetime.utcnow()
#         )
#     )
#     reset_token = result.scalar_one_or_none()

#     if not reset_token:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired reset token"
#         )

#     # Get user
#     result = await db.execute(
#         select(User).where(User.id == reset_token.user_id)
#     )
#     user = result.scalar_one_or_none()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )

#     # Update password
#     user.hashed_password = hash_password(reset_data.new_password)
#     user.password_changed_at = datetime.utcnow()

#     # Mark token as used
#     reset_token.used = True
#     reset_token.used_at = datetime.utcnow()

#     # Revoke all refresh tokens
#     stmt = (
#         update(RefreshToken)
#         .where(RefreshToken.user_id == user.id)
#         .values(
#             revoked=True,
#             revoked_at=datetime.utcnow()
#         )
#     )
#     await db.execute(stmt)

#     await db.commit()

#     return {"message": "Password reset successful. Please login with your new password."}


# @router.get("/me", response_model=UserResponse)
# async def get_me(
#     current_user: User = Depends(get_current_user)
# ):
#     """Get current user info"""
#     return current_user


# @router.post("/verify-token")
# async def verify_token(
#     current_user: User = Depends(get_current_user),
#     token: str = Depends(oauth2_scheme),
#     redis_client: redis.Redis = Depends(get_redis)
# ):
#     """
#     Verify if token is valid

#     - Checks if token is blacklisted
#     - Returns user info if valid
#     """
#     # Check if token is blacklisted
#     if await is_token_blacklisted(token, redis_client):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has been revoked"
#         )

#     return {
#         "valid": True,
#         "user_id": current_user.id,
#         "username": current_user.username,
#         "email": current_user.email,
#         "role": current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
#         "is_active": current_user.is_active,
#         "email_verified": current_user.email_verified
#     }


# @router.post("/resend-verification")
# async def resend_verification_email(
#     email: str,
#     db: AsyncSession = Depends(get_db_connection),
#     redis_client: redis.Redis = Depends(get_redis)
# ):
#     """
#     Resend email verification

#     - Rate limited to 3 per hour
#     - Only for unverified emails
#     """
#     # Rate limiting
#     if not await check_rate_limit(
#         redis_client,
#         f"resend_verification:{email}",
#         max_attempts=3,
#         window_seconds=3600
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#             detail="Too many verification requests. Please try again later."
#         )

#     # Find user
#     result = await db.execute(
#         select(User).where(User.email == email.lower())
#     )
#     user = result.scalar_one_or_none()

#     if not user:
#         # Don't reveal if email exists
#         return {"message": "If the email exists and is unverified, a new verification email has been sent."}

#     if user.email_verified:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email already verified"
#         )

#     # Invalidate old tokens
#     stmt = (
#         update(EmailVerificationToken)
#         .where(
#             EmailVerificationToken.user_id == user.id,
#             EmailVerificationToken.used == False
#         )
#         .values(
#             used=True,
#             used_at=datetime.utcnow()
#         )
#     )
#     await db.execute(stmt)

#   # ... continuación desde resend_verification_email

#     # Create new verification token
#     verification_token = secrets.token_urlsafe(32)
#     email_token = EmailVerificationToken(
#         id=str(uuid.uuid4()),
#         token=hashlib.sha256(verification_token.encode()).hexdigest(),
#         user_id=user.id,
#         expires_at=datetime.utcnow() + timedelta(hours=24),
#         used=False
#     )
#     db.add(email_token)
#     await db.commit()

#     # Send verification email
#     asyncio.create_task(send_verification_email(
#         user.email, verification_token))

#     return {"message": "If the email exists and is unverified, a new verification email has been sent."}


# @router.get("/sessions")
# async def get_active_sessions(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """
#     Get all active sessions/refresh tokens for current user

#     - Shows device info and last activity
#     - Allows user to see where they're logged in
#     """
#     result = await db.execute(
#         select(RefreshToken).where(
#             RefreshToken.user_id == current_user.id,
#             RefreshToken.revoked == False,
#             RefreshToken.expires_at > datetime.utcnow()
#         ).order_by(RefreshToken.created_at.desc())
#     )
#     sessions = result.scalars().all()

#     return {
#         "active_sessions": [
#             {
#                 "id": session.id,
#                 "created_at": session.created_at,
#                 "last_used": session.last_used,
#                 "ip_address": session.ip_address,
#                 "user_agent": session.user_agent,
#                 "expires_at": session.expires_at
#             }
#             for session in sessions
#         ]
#     }


# @router.delete("/sessions/{session_id}")
# async def revoke_session(
#     session_id: str,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """
#     Revoke a specific session/refresh token

#     - Allows user to logout specific devices
#     """
#     result = await db.execute(
#         select(RefreshToken).where(
#             RefreshToken.id == session_id,
#             RefreshToken.user_id == current_user.id,
#             RefreshToken.revoked == False
#         )
#     )
#     session = result.scalar_one_or_none()

#     if not session:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Session not found or already revoked"
#         )

#     session.revoked = True
#     session.revoked_at = datetime.utcnow()
#     await db.commit()

#     return {"message": "Session revoked successfully"}


# @router.post("/enable-2fa")
# async def enable_two_factor(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """
#     Enable two-factor authentication

#     - Generates TOTP secret
#     - Returns QR code for authenticator apps
#     """
#     import pyotp
#     import qrcode
#     import io
#     import base64

#     if current_user.two_factor_enabled:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Two-factor authentication already enabled"
#         )

#     # Generate secret
#     secret = pyotp.random_base32()

#     # Generate provisioning URI
#     totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
#         name=current_user.email,
#         issuer_name="YourApp"
#     )

#     # Generate QR code
#     qr = qrcode.QRCode(version=1, box_size=10, border=5)
#     qr.add_data(totp_uri)
#     qr.make(fit=True)

#     img = qr.make_image(fill_color="black", back_color="white")
#     buf = io.BytesIO()
#     img.save(buf, format='PNG')
#     buf.seek(0)

#     # Convert to base64
#     qr_code = base64.b64encode(buf.getvalue()).decode()

#     # Store secret (encrypted in production)
#     current_user.two_factor_secret = secret
#     current_user.two_factor_enabled = False  # Not enabled until verified
#     await db.commit()

#     return {
#         "secret": secret,
#         "qr_code": f"data:image/png;base64,{qr_code}",
#         "manual_entry": totp_uri
#     }


# @router.post("/verify-2fa")
# async def verify_two_factor(
#     code: str,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """
#     Verify and activate two-factor authentication

#     - Validates TOTP code
#     - Generates backup codes
#     """
#     import pyotp

#     if not current_user.two_factor_secret:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Two-factor authentication not initialized"
#         )

#     # Verify code
#     totp = pyotp.TOTP(current_user.two_factor_secret)
#     if not totp.verify(code, valid_window=1):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid verification code"
#         )

#     # Generate backup codes
#     backup_codes = [secrets.token_hex(4) for _ in range(10)]

#     # Store hashed backup codes
#     current_user.two_factor_enabled = True
#     current_user.two_factor_backup_codes = ",".join([
#         hashlib.sha256(code.encode()).hexdigest()
#         for code in backup_codes
#     ])
#     await db.commit()

#     return {
#         "message": "Two-factor authentication enabled successfully",
#         "backup_codes": backup_codes
#     }


# @router.post("/disable-2fa")
# async def disable_two_factor(
#     password: str,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """
#     Disable two-factor authentication

#     - Requires password confirmation
#     """
#     if not current_user.two_factor_enabled:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Two-factor authentication not enabled"
#         )

#     # Verify password
#     if not verify_password(password, current_user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect password"
#         )

#     # Disable 2FA
#     current_user.two_factor_enabled = False
#     current_user.two_factor_secret = None
#     current_user.two_factor_backup_codes = None
#     await db.commit()

#     return {"message": "Two-factor authentication disabled"}


# @router.post("/verify-2fa-login")
# async def verify_two_factor_login(
#     code: str,
#     user_id: str,
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """
#     Verify 2FA code during login

#     - Called after successful password authentication
#     - Validates TOTP or backup code
#     """
#     import pyotp

#     # Get user
#     result = await db.execute(
#         select(User).where(User.id == user_id)
#     )
#     user = result.scalar_one_or_none()

#     if not user or not user.two_factor_enabled:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid request"
#         )

#     # Try TOTP first
#     totp = pyotp.TOTP(user.two_factor_secret)
#     if totp.verify(code, valid_window=1):
#         return {"valid": True, "method": "totp"}

#     # Try backup codes
#     if user.two_factor_backup_codes:
#         backup_codes = user.two_factor_backup_codes.split(",")
#         code_hash = hashlib.sha256(code.encode()).hexdigest()

#         if code_hash in backup_codes:
#             # Remove used backup code
#             backup_codes.remove(code_hash)
#             user.two_factor_backup_codes = ",".join(backup_codes)
#             await db.commit()
#             return {"valid": True, "method": "backup_code"}

#     raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid authentication code"
#     )


# @router.get("/check-username/{username}")
# async def check_username_availability(
#     username: str,
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """
#     Check if username is available

#     - Public endpoint for registration form
#     """
#     if len(username) < 3:
#         return {
#             "available": False,
#             "message": "Username must be at least 3 characters"
#         }

#     result = await db.execute(
#         select(func.count(User.id)).where(
#             User.username == username.lower()
#         )
#     )
#     exists = result.scalar() > 0

#     return {
#         "available": not exists,
#         "message": "Username already taken" if exists else "Username available"
#     }


# @router.get("/check-email/{email}")
# async def check_email_availability(
#     email: str,
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """
#     Check if email is available

#     - Public endpoint for registration form
#     """
#     import re

#     # Basic email validation
#     email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     if not re.match(email_pattern, email):
#         return {
#             "available": False,
#             "message": "Invalid email format"
#         }

#     result = await db.execute(
#         select(func.count(User.id)).where(
#             User.email == email.lower()
#         )
#     )
#     exists = result.scalar() > 0

#     return {
#         "available": not exists,
#         "message": "Email already registered" if exists else "Email available"
#     }


# @router.post("/request-account-deletion")
# async def request_account_deletion(
#     password: str,
#     reason: Optional[str] = None,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """
#     Request account deletion

#     - Requires password confirmation
#     - Schedules deletion after 30 days (soft delete)
#     """
#     # Verify password
#     if not verify_password(password, current_user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect password"
#         )

#     # Schedule deletion
#     current_user.deletion_requested_at = datetime.utcnow()
#     current_user.deletion_scheduled_for = datetime.utcnow() + timedelta(days=30)
#     current_user.deletion_reason = reason

#     await db.commit()

#     return {
#         "message": "Account deletion scheduled",
#         "scheduled_for": current_user.deletion_scheduled_for,
#         "note": "You can cancel this request within 30 days by logging in"
#     }


# @router.post("/cancel-account-deletion")
# async def cancel_account_deletion(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db_connection)
# ):
#     """Cancel account deletion request"""
#     if not current_user.deletion_requested_at:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="No deletion request found"
#         )

#     current_user.deletion_requested_at = None
#     current_user.deletion_scheduled_for = None
#     current_user.deletion_reason = None

#     await db.commit()

#     return {"message": "Account deletion cancelled"}
