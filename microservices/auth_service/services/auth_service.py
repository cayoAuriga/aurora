# services/auth_service.py
from fastapi import HTTPException
from typing import Callable
from datetime import datetime, timedelta
import requests
import uuid
from models.entities import SessionModel
from repositories.session_repository import SessionRepository
from sqlalchemy.orm import Session as SQLSession
from models.entities import User
from repositories.user_repository import UserRepository

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
CLIENT_ID = "<your-client-id>"
CLIENT_SECRET = "<your-client-secret>"
REDIRECT_URI = "<your-redirect-uri>"

def exchange_google_code_fn(
    user_repo: UserRepository,
    session_repo: SessionRepository,
    db: SQLSession,
    code: str,
    code_verifier: str
) -> SessionModel:
    """Intercambia code + code_verifier por tokens y crea sesión"""
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier
    }
    resp = requests.post(GOOGLE_TOKEN_URL, data=payload)
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
    tokens = resp.json()
    
    # Obtener info del usuario desde Google
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    user_info = requests.get(GOOGLE_USERINFO_URL, headers=headers).json()
    
    # Crear o actualizar usuario en MySQL
    user = user_repo.get_by_email(db, user_info["email"])
    if not user:
        user = user_repo.create(db, {
            "email": user_info["email"],
            "name": user_info.get("name"),
            "picture": user_info.get("picture")
        })
    
    # Crear sesión en MongoDB
    session = SessionModel(
        session_id=str(uuid.uuid4()),
        user_id=user.id,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(seconds=int(tokens["expires_in"])),
        client_ip=None,
        user_agent=None
    )
    return session_repo.create(session)
