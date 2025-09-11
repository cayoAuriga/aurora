# main.py
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from config import service_config
from routers import auth_router
# from middleware.rate_limit import RateLimitMiddleware
# from middleware.security import SecurityHeadersMiddleware

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager para startup y shutdown
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Handle application startup and shutdown"""
#     # Startup
#     logger.info("Starting up Auth Service...")
#     await init_db()
#     logger.info("Database initialized")
    
#     yield
    
#     # Shutdown
#     logger.info("Shutting down Auth Service...")
#     await close_db()
#     logger.info("Database connections closed")

# Crear aplicación FastAPI
app = FastAPI(
    title="Auth Service",
    description="Authentication and user management service with JWT tokens, 2FA, and advanced security features",
    version="1.0.0",
    docs_url="/docs" if service_config.environment != "production" else None,
    redoc_url="/redoc" if service_config.environment != "production" else None,
    openapi_url="/openapi.json" if service_config.environment != "production" else None,
    # lifespan=lifespan
)

# Middleware de seguridad
if service_config.environment == "production":
    # Solo en producción - verificar hosts confiables
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=service_config.cors_origins  # ["example.com", "*.example.com"]
    )

# CORS Middleware - IMPORTANTE: debe ser añadido antes que otros middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=service_config.cors_origins,  # ["http://localhost:3000", "https://example.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"],
)

# Rate Limiting Middleware
# app.add_middleware(RateLimitMiddleware)

# Security Headers Middleware (si lo tienes)
# app.add_middleware(SecurityHeadersMiddleware)

# Request ID Middleware para tracking
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(
        f"Request started: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate process time
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    # Log response
    logger.info(
        f"Request completed: {request.method} {request.url.path} "
        f"status={response.status_code} duration={process_time:.3f}s"
    )
    
    # Add process time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Include routers
app.include_router(auth_router.router, prefix="/api/v1")
# app.include_router(users_router.router, prefix="/api/v1")

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint - returns service info"""
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": "/docs" if service_config.environment != "production" else "Disabled in production"
    }

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    
    Returns:
        - Service status
        - Database connectivity
        - Redis connectivity
    """
    from database import get_db, get_redis
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Auth Service",
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check database
    try:
        async for db in get_db():
            await db.execute("SELECT 1")
            health_status["checks"]["database"] = "connected"
            break
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        async for redis_client in get_redis():
            await redis_client.ping()
            health_status["checks"]["redis"] = "connected"
            break
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = f"error: {str(e)}"
    
    return health_status

# Ready check endpoint (for k8s readiness probe)
@app.get("/ready", tags=["health"])
async def ready_check():
    """
    Readiness check endpoint
    
    Used by orchestrators to determine if the service is ready to accept traffic
    """
    # Perform the same checks as health
    health_result = await health_check()
    
    if health_result["status"] == "healthy":
        return {"ready": True}
    else:
        return {"ready": False}, 503

# Metrics endpoint (basic)
@app.get("/metrics", tags=["monitoring"])
async def metrics():
    """
    Basic metrics endpoint
    
    In production, consider using Prometheus client
    """
    from database import get_db
    from models import User, RefreshToken
    from sqlalchemy import select, func
    
    metrics_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {}
    }
    
    try:
        async for db in get_db():
            # Count users
            user_count = await db.execute(select(func.count(User.id)))
            metrics_data["metrics"]["total_users"] = user_count.scalar()
            
            # Count active users (logged in last 30 days)
            from datetime import timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_users = await db.execute(
                select(func.count(User.id)).where(User.last_login > thirty_days_ago)
            )
            metrics_data["metrics"]["active_users"] = active_users.scalar()
            
            # Count active sessions
            active_sessions = await db.execute(
                select(func.count(RefreshToken.id)).where(
                    RefreshToken.revoked == False,
                    RefreshToken.expires_at > datetime.utcnow()
                )
            )
            metrics_data["metrics"]["active_sessions"] = active_sessions.scalar()
            
            break
    except Exception as e:
        metrics_data["error"] = str(e)
    
    return metrics_data

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return {
        "error": "Not Found",
        "message": f"The path {request.url.path} was not found",
        "status_code": 404
    }

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "status_code": 500
    }

# Main entry point
if __name__ == "__main__":
    # Configuración para desarrollo
    uvicorn.run(
        "main:app",  # Importante: usar string para hot reload
        host=service_config.host,
        port=service_config.service_port,
        reload=service_config.environment == "development",
        log_level="info" if service_config.environment == "production" else "debug",
        access_log=True,
        workers=1 if service_config.environment == "development" else 4
    )