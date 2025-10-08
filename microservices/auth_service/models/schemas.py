# models/schemas/user_schemas.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from fastapi import Request

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
    
    @field_validator("roles", mode="before")
    @classmethod
    def roles_to_str(cls, v):
        #The value 'v' will be a list of Role ORM objects
        if v and isinstance(v[0], Role):
            return [r.name for r in v]
        # If it's already a list of strings or empty, just return it
        return v

    class Config:
       from_attributes = True

# --- Auth Provider ---

class AuthProviderBase(BaseModel):
    provider: str
    provider_user_id: str
    user_id: int

class AuthProviderCreate(AuthProviderBase):
    pass

class AuthProviderRead(AuthProviderBase):
    id: int

    class Config:
       from_attributes = True

# --- ROLES ---
class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: int
    permissions: List[str] = []

    @field_validator("permissions", mode="before")
    @classmethod
    def permissions_to_str(cls, v):
        if v and isinstance(v[0], Permission):
            return [p.name for p in v]
        return v

    class Config:
       from_attributes = True

class RoleUpdate(BaseModel):
    name: Optional[str]
    permissions: Optional[List[str]] = []
    
# --- PERMISOS ---
class PermissionBase(BaseModel):
    name: str
    description: Optional[str]

class PermissionCreate(PermissionBase):
    pass

class PermissionRead(PermissionBase):
    id: int

    class Config:
       from_attributes = True
class PermissionUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    
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

#--- CONTEXTO DE AUTENTICACIÓN GOOGLE ---
class GoogleAuthContext(BaseModel):
    code: str
    code_verifier: str
    request: Request

    class Config:
        arbitrary_types_allowed = True