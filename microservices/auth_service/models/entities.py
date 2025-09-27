from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# --- MODELOS ORM ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    picture = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    providers = relationship("AuthProvider", back_populates="user")
    roles = relationship("Role", secondary="user_roles", back_populates="users")


class AuthProvider(Base):
    __tablename__ = "auth_providers"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)  # "google"
    provider_user_id = Column(String(255), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="providers")

# -- relaciones muchos a muchos para roles y permisos --
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # ej: "read:users"
    description = Column(String(255), nullable=True)

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


# Tablas puente
class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)

# --- Mongodb Session Model ---    
class SessionModel(BaseModel):
    session_id: str
    user_id: int
    access_token: str
    refresh_token: str
    created_at: datetime = datetime.utcnow()
    expires_at: datetime
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None