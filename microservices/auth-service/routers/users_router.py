from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import User, UserResponse, UserUpdate, UserCreate, UserRole
from dependencies import require_admin, require_role, get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of users to return"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in email and username"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users (admin only)
    
    - **skip**: Number of users to skip for pagination
    - **limit**: Maximum number of users to return
    - **role**: Filter by user role
    - **is_active**: Filter by active status
    - **search**: Search term for email/username
    """
    query = select(User)
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_term)) | 
            (User.username.ilike(search_term))
        )
    
    # Apply pagination and ordering
    query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    return users

@router.get("/count")
async def get_users_count(
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get total count of users (admin only)"""
    query = select(func.count(User.id))
    
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    result = await db.execute(query)
    count = result.scalar()
    
    return {"total": count, "filters": {"role": role, "is_active": is_active}}

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID
    
    Users can only get their own info unless they're admin
    """
    # Check permissions
    if str(current_user.id) != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this user"
        )
    
    # Get user
    result = await db.execute(
        select(User).filter(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return user

@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's own information"""
    # Prevent users from changing their own role
    if user_update.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change your own role"
        )
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True, exclude_none=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        stmt = (
            update(User)
            .where(User.id == current_user.id)
            .values(**update_data)
        )
        await db.execute(stmt)
        await db.commit()
        
        # Refresh user object
        await db.refresh(current_user)
    
    return current_user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user information
    
    - Users can only update their own info unless they're admin
    - Only admins can change roles and active status
    """
    # Check permissions
    if str(current_user.id) != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user"
        )
    
    # Get user
    result = await db.execute(
        select(User).filter(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Only admins can change roles and active status
    if (user_update.role or user_update.is_active is not None) and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change user roles and active status"
        )
    
    # Prevent admins from removing their own admin role
    if str(current_user.id) == user_id and user_update.role and user_update.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove your own admin role"
        )
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True, exclude_none=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
    
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user (admin only)
    
    Soft delete by default (sets is_active=False)
    """
    # Prevent self-deletion
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Get user
    result = await db.execute(
        select(User).filter(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Soft delete (deactivate)
    user.is_active = False
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "message": f"User {user_id} has been deactivated",
        "user_id": user_id
    }

@router.delete("/{user_id}/permanent")
async def delete_user_permanent(
    user_id: str,
    confirm: bool = Query(False, description="Confirm permanent deletion"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Permanently delete user (admin only)
    
    **Warning**: This action cannot be undone!
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please confirm permanent deletion by setting confirm=true"
        )
    
    # Prevent self-deletion
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Check if user exists
    result = await db.execute(
        select(User).filter(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Permanent delete
    await db.execute(
        delete(User).where(User.id == user_id)
    )
    await db.commit()
    
    return {
        "message": f"User {user_id} has been permanently deleted",
        "user_id": user_id
    }

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Activate a deactivated user (admin only)"""
    result = await db.execute(
        select(User).filter(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active"
        )
    
    user.is_active = True
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    return {
        "message": f"User {user_id} has been activated",
        "user": UserResponse.from_orm(user)
    }

@router.post("/{user_id}/change-role")
async def change_user_role(
    user_id: str,
    new_role: UserRole,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Change user role (admin only)"""
    # Prevent changing own role
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role. Ask another admin."
        )
    
    result = await db.execute(
        select(User).filter(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    if user.role == new_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User already has role {new_role}"
        )
    
    old_role = user.role
    user.role = new_role
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    return {
        "message": f"User role changed from {old_role} to {new_role}",
        "user": UserResponse.from_orm(user)
    }

@router.get("/{user_id}/exists")
async def check_user_exists(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Check if a user exists (public endpoint)"""
    result = await db.execute(
        select(func.count(User.id)).filter(User.id == user_id)
    )
    exists = result.scalar() > 0
    
    return {"exists": exists, "user_id": user_id}