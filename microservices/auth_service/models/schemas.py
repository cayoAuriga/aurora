# models/schemas/user_schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- USUARIO ---
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str]

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str]
    password: Optional[str]
    is_active: Optional[bool]

class UserRead(UserBase):
    id: int
    is_active: bool
    roles: List[str] = []

    class Config:
        orm_mode = True

# --- ROLES ---
class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: int
    permissions: List[str] = []

    class Config:
        orm_mode = True

# --- PERMISOS ---
class PermissionBase(BaseModel):
    name: str
    description: Optional[str]

class PermissionCreate(PermissionBase):
    pass

class PermissionRead(PermissionBase):
    id: int

    class Config:
        orm_mode = True

# --- SESIONES (MongoDB) ---
class SessionBase(BaseModel):
    session_id: str
    user_id: int
    access_token: str
    refresh_token: str
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

class SessionCreate(SessionBase):
    expires_at: datetime

class SessionRead(SessionBase):
    created_at: datetime
    expires_at: datetime
