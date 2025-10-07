# routers/auth_router.py
from fastapi import APIRouter, Depends, Form, Request
from dependencies import get_auth_service, get_uow
from services.auth_service import AuthService, GoogleAuthContext
from repositories.unit_of_work import AbstractUnitOfWork


auth_router = APIRouter()

@auth_router.post("/auth/google/callback")
def google_callback(
    request: Request, # Inyectamos el objeto Request
    code: str = Form(...),
    code_verifier: str = Form(...),
    uow: AbstractUnitOfWork = Depends(get_uow),    
    auth_service = Depends(get_auth_service),    
):
    """Callback de Google OAuth2 con PKCE"""
    context = GoogleAuthContext(code=code, code_verifier=code_verifier, request=request)
    session = auth_service[AuthService.AUTHENTICATE_GOOGLE](uow, context=context)
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "expires_at": session.expires_at
    }
