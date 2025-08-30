"""
Base FastAPI application template for microservices
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from typing import Optional
import uuid

from .logging import get_logger
from .error_handling import ServiceException, create_http_exception


class BaseService:
    """Base class for microservice applications"""
    
    def __init__(
        self, 
        service_name: str, 
        version: str = "1.0.0",
        description: Optional[str] = None
    ):
        self.service_name = service_name
        self.version = version
        self.description = description or f"{service_name} microservice"
        self.logger = get_logger(service_name)
        
        # Create FastAPI app
        self.app = FastAPI(
            title=service_name,
            version=version,
            description=self.description
        )
        
        # Add middleware
        self._setup_middleware()
        
        # Add exception handlers
        self._setup_exception_handlers()
        
        # Add health check endpoint
        self._setup_health_check()
    
    def _setup_middleware(self):
        """Setup common middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
            
            # Add correlation ID to request state
            request.state.correlation_id = correlation_id
            
            # Log request
            self.logger.info(
                f"Incoming request: {request.method} {request.url.path}",
                correlation_id=correlation_id,
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params)
            )
            
            response = await call_next(request)
            
            # Log response
            self.logger.info(
                f"Response: {response.status_code}",
                correlation_id=correlation_id,
                status_code=response.status_code
            )
            
            # Add correlation ID to response headers
            response.headers["x-correlation-id"] = correlation_id
            
            return response
    
    def _setup_exception_handlers(self):
        """Setup exception handlers"""
        
        @self.app.exception_handler(ServiceException)
        async def service_exception_handler(request: Request, exc: ServiceException):
            correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
            
            self.logger.error(
                f"Service exception: {exc.message}",
                correlation_id=correlation_id,
                error_code=exc.error_code,
                details=exc.details
            )
            
            return JSONResponse(
                status_code=400,
                content=exc.to_error_response().dict(),
                headers={"x-correlation-id": correlation_id}
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
            
            self.logger.error(
                f"Unhandled exception: {str(exc)}",
                correlation_id=correlation_id,
                exception_type=type(exc).__name__
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "error_message": "An internal server error occurred",
                    "correlation_id": correlation_id,
                    "service_name": self.service_name
                },
                headers={"x-correlation-id": correlation_id}
            )
    
    def _setup_health_check(self):
        """Setup health check endpoint"""
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": self.service_name,
                "version": self.version,
                "timestamp": "2024-01-01T00:00:00Z"  # Will be replaced with actual timestamp
            }
        
        @self.app.get("/health/ready")
        async def readiness_check():
            # Override this method in subclasses to add specific readiness checks
            return {
                "status": "ready",
                "service": self.service_name,
                "checks": {
                    "database": "ok",  # Override in subclasses
                    "dependencies": "ok"
                }
            }
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance"""
        return self.app
    
    def add_router(self, router, prefix: str = "", tags: list = None):
        """Add a router to the application"""
        self.app.include_router(router, prefix=prefix, tags=tags or [])


def create_service_app(
    service_name: str, 
    version: str = "1.0.0", 
    description: Optional[str] = None
) -> BaseService:
    """Factory function to create a microservice application"""
    return BaseService(service_name, version, description)