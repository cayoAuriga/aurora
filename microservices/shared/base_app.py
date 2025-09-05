"""
Base FastAPI application template for Aurora microservices
"""
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid
import logging

from .config import BaseServiceConfig
from .aurora_logging import setup_logging, log_request
from .errors import BaseServiceException, create_error_response
from .database import health_check, async_health_check


class BaseService:
    """Base service class for all microservices"""
    
    def __init__(
        self,
        service_name: str,
        config: BaseServiceConfig,
        title: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "1.0.0"
    ):
        self.service_name = service_name
        self.config = config
        self.logger = setup_logging(
            service_name=service_name,
            level=config.log_level,
            use_json=config.environment != "development"
        )
        
        # Create FastAPI app with lifespan
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self.logger.info(f"Starting {service_name} service")
            await self.startup()
            yield
            # Shutdown
            self.logger.info(f"Shutting down {service_name} service")
            await self.shutdown()
        
        self.app = FastAPI(
            title=title or f"{service_name.title()} Service",
            description=description or f"Aurora {service_name} microservice",
            version=version,
            lifespan=lifespan
        )
        
        self._setup_middleware()
        self._setup_exception_handlers()
        self._setup_health_endpoints()
    
    def _setup_middleware(self):
        """Set up FastAPI middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware
        if self.config.environment == "production":
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=["*"]  # Configure based on your needs
            )
        
        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            # Generate correlation ID
            correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
            
            # Add correlation ID to request state
            request.state.correlation_id = correlation_id
            
            start_time = time.time()
            
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            process_time = (time.time() - start_time) * 1000
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            # Log request
            log_request(
                logger=self.logger,
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                response_time_ms=process_time,
                correlation_id=correlation_id,
                user_agent=request.headers.get("User-Agent"),
                ip_address=request.client.host if request.client else None
            )
            
            return response
    
    def _setup_exception_handlers(self):
        """Set up exception handlers"""
        
        @self.app.exception_handler(BaseServiceException)
        async def service_exception_handler(request: Request, exc: BaseServiceException):
            correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
            exc.correlation_id = correlation_id
            
            error_response = create_error_response(exc, self.service_name)
            
            self.logger.error(
                f"Service exception: {exc.message}",
                extra={
                    "error_code": exc.error_code,
                    "correlation_id": correlation_id,
                    "status_code": exc.status_code
                }
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content=error_response.dict()
            )
        
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
            
            self.logger.error(
                f"HTTP exception: {exc.detail}",
                extra={
                    "correlation_id": correlation_id,
                    "status_code": exc.status_code
                }
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error_code": "HTTP_ERROR",
                    "error_message": str(exc.detail),
                    "correlation_id": correlation_id,
                    "timestamp": time.time(),
                    "service_name": self.service_name
                }
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
            
            self.logger.error(
                f"Unhandled exception: {str(exc)}",
                extra={
                    "correlation_id": correlation_id,
                    "exception_type": type(exc).__name__
                },
                exc_info=True
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "error_message": "An internal server error occurred",
                    "correlation_id": correlation_id,
                    "timestamp": time.time(),
                    "service_name": self.service_name
                }
            )
    
    def _setup_health_endpoints(self):
        """Set up health check endpoints"""
        from .health_checks import create_standard_health_checks
        from .service_discovery import get_discovery_client
        
        # Create health check manager
        self.health_manager = create_standard_health_checks(
            self.service_name,
            get_discovery_client()
        )
        
        @self.app.get("/health")
        async def health_check_endpoint():
            """Basic health check"""
            return {
                "status": "healthy",
                "service": self.service_name,
                "timestamp": time.time()
            }
        
        @self.app.get("/health/ready")
        async def readiness_check():
            """Readiness check including dependencies"""
            try:
                health_status = await self.health_manager.get_overall_health()
                status_code = 200 if health_status["status"] == "healthy" else 503
                
                return JSONResponse(
                    status_code=status_code,
                    content=health_status
                )
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "service": self.service_name,
                        "error": str(e),
                        "timestamp": time.time()
                    }
                )
        
        @self.app.get("/health/live")
        async def liveness_check():
            """Liveness check"""
            return {
                "status": "alive",
                "service": self.service_name,
                "timestamp": time.time()
            }
        
        @self.app.get("/health/detailed")
        async def detailed_health_check():
            """Detailed health check with all components"""
            try:
                health_status = await self.health_manager.get_overall_health(use_cache=False)
                status_code = 200 if health_status["status"] in ["healthy", "degraded"] else 503
                
                return JSONResponse(
                    status_code=status_code,
                    content=health_status
                )
            except Exception as e:
                self.logger.error(f"Detailed health check failed: {e}")
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "service": self.service_name,
                        "error": str(e),
                        "timestamp": time.time()
                    }
                )
    
    async def startup(self):
        """Service startup logic - override in subclasses"""
        from .service_discovery import get_discovery_client
        
        # Register service with discovery
        try:
            discovery_client = get_discovery_client()
            await discovery_client.register_self(
                service_name=self.service_name,
                host=self.config.host,
                port=self.config.service_port,
                health_endpoint="/health/ready",
                metadata={
                    "version": "1.0.0",
                    "environment": self.config.environment,
                    "started_at": time.time()
                }
            )
            self.logger.info(f"Registered {self.service_name} with service discovery")
        except Exception as e:
            self.logger.error(f"Failed to register with service discovery: {e}")
    
    async def shutdown(self):
        """Service shutdown logic - override in subclasses"""
        from .service_discovery import get_discovery_client, cleanup_discovery
        
        # Deregister service
        try:
            discovery_client = get_discovery_client()
            await discovery_client.registry.deregister_service(self.service_name)
            self.logger.info(f"Deregistered {self.service_name} from service discovery")
        except Exception as e:
            self.logger.error(f"Failed to deregister from service discovery: {e}")
        
        # Cleanup discovery clients
        try:
            await cleanup_discovery()
        except Exception as e:
            self.logger.error(f"Failed to cleanup discovery clients: {e}")
    
    def add_router(self, router, prefix: str = "", tags: Optional[List[str]] = None):
        """Add a router to the application"""
        self.app.include_router(router, prefix=prefix, tags=tags)
    
    def get_correlation_id_dependency(self):
        """Dependency to get correlation ID from request"""
        def get_correlation_id(request: Request) -> str:
            return getattr(request.state, "correlation_id", str(uuid.uuid4()))
        
        return get_correlation_id


def create_service(
    service_name: str,
    config: BaseServiceConfig,
    title: Optional[str] = None,
    description: Optional[str] = None,
    version: str = "1.0.0"
) -> BaseService:
    """Factory function to create a service"""
    return BaseService(
        service_name=service_name,
        config=config,
        title=title,
        description=description,
        version=version
    )


# Utility functions for common patterns
def get_current_user_dependency():
    """Dependency to get current user (placeholder)"""
    def get_current_user(request: Request):
        # This would typically validate JWT token and return user info
        # For now, return a placeholder
        return {"id": 1, "username": "test_user"}
    
    return get_current_user


def require_auth_dependency():
    """Dependency that requires authentication"""
    def require_auth(current_user = Depends(get_current_user_dependency())):
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        return current_user
    
    return require_auth


def get_pagination_params(skip: int = 0, limit: int = 100):
    """Common pagination parameters"""
    return {"skip": skip, "limit": min(limit, 1000)}  # Max 1000 items per page