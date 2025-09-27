# routers/auth_router.py
from fastapi import APIRouter, Depends, Form
from dependencies import get_auth_service, get_user_repository, get_session_repository
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter()

@router.post("/auth/google/callback")
def google_callback(
    code: str = Form(...),
    code_verifier: str = Form(...),
    db: Session = Depends(get_db),
    auth_service = Depends(lambda: get_auth_service(
        user_repo=get_user_repository(),
        session_repo=get_session_repository()
    ))
):
    """Callback de Google OAuth2 con PKCE"""
    session = auth_service["exchange_google_code"](db, code, code_verifier)
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "expires_at": session.expires_at
    }
