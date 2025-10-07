import requests
from enum import Enum
from typing import Dict, Callable, Optional
from fastapi import HTTPException, status, Request
import functools
from models.schemas import SessionRead, UserCreate, GoogleAuthContext, AuthProviderCreate
from repositories.unit_of_work import AbstractUnitOfWork
from services.session_service import SessionService
from services.user_service import UserService
from shared.settings import GoogleOAuthConfig # Importamos la configuración


class AuthService(str, Enum):
    AUTHENTICATE_GOOGLE = "authenticate_with_google"

# --- Funciones Auxiliares (Implementación "How") ---

def _exchange_code_for_tokens(
    code: str, code_verifier: str, config: GoogleOAuthConfig
) -> Dict:
    """Paso 1: Intercambia el código de autorización por tokens de acceso."""
    payload = {
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": config.redirect_uri,
        "code_verifier": code_verifier,
    }
    resp = requests.post(config.token_url, data=payload)
    if resp.status_code != 200:
        # Log the error from Google for debugging
        # logger.error(f"Google token exchange failed: {resp.json()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange authorization code for tokens.",
        )
    return resp.json()


def _get_google_user_info(access_token: str, config: GoogleOAuthConfig) -> Dict:
    """Paso 2: Obtiene la información del usuario desde Google."""
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(config.userinfo_url, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve user information from provider.",
        )
    return resp.json()


def _get_or_create_user_from_provider(
    uow: AbstractUnitOfWork, user_info: Dict
) -> "User":
    """
    Busca o crea el usuario y el proveedor de autenticación asociado.
    Toda esta lógica se ejecuta dentro de una única transacción gracias al UoW.
    """
    provider_name = "google"
    provider_user_id = user_info["sub"]

    with uow:
        # 1. Busca si ya existe la conexión proveedor-usuario (la forma más eficiente)
        auth_provider = uow.auth_providers.get_by_provider_user_id(
            provider=provider_name, provider_user_id=provider_user_id
        )
        if auth_provider:
            # Si existe, devolvemos el usuario asociado y terminamos.
            return auth_provider.user

        # 2. Si no existe, busca si el usuario ya tiene una cuenta con ese email
        user = uow.users.get_by_email(email=user_info["email"])
        if not user:
            # 3. Si el usuario no existe en absoluto, lo creamos
            import secrets
            user_data = UserCreate(
                email=user_info["email"],
                name=user_info.get("name"),
                password=secrets.token_urlsafe(16), # Contraseña no usable
            )
            user = uow.users.create(user_data)

        # 4. (¡Paso clave!) Crea el registro en AuthProvider y lo vincula al usuario
        auth_provider_data = AuthProviderCreate(
            provider=provider_name,
            provider_user_id=provider_user_id,
            user_id=user.id,
        )
        uow.auth_providers.create(auth_provider_data)
        
        # El commit es manejado por el UoW al salir del bloque 'with'
        return user

# --- Función Principal del Servicio (Declarativa "What") ---

def authenticate_with_google_fn(
    # Las dependencias se "inyectarán" a través de partial
    uow: AbstractUnitOfWork,
    session_service: Dict[str, Callable],
    session_repo,
    config: GoogleOAuthConfig,
    # --- Argumentos de ejecución ---
    context: GoogleAuthContext,
) -> SessionRead:
    """Orquesta el flujo de autenticación. Las dependencias son inyectadas."""
    # ... (el cuerpo de la función no cambia en absoluto)
    tokens = _exchange_code_for_tokens(context.code, context.code_verifier, config)
    user_info = _get_google_user_info(tokens["access_token"], config)
    user = _get_or_create_user_from_provider(uow, user_info)
    session = session_service[SessionService.CREATE](
        repo=session_repo,
        user_id=user.id,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        expires_in=tokens.get("expires_in", 3600),
        client_ip=context.request.client.host,
        user_agent=context.request.headers.get("user-agent"),
    )
    return session

# --- La Factoría ahora ACEPTA dependencias ---
def create_auth_service(
    session_service: Dict[str, Callable],
    session_repo, # El repo que necesita el session_service
    config: GoogleOAuthConfig,
) -> Dict[str, Callable]:
    """
    Factory que ACEPTA dependencias y devuelve funciones pre-configuradas.
    """
    # Creamos una versión de la función con las dependencias ya aplicadas
    configured_auth_fn = functools.partial(
        authenticate_with_google_fn,
        session_service=session_service,
        session_repo=session_repo,
        config=config,
    )

    return {
        AuthService.AUTHENTICATE_GOOGLE: configured_auth_fn,
    }