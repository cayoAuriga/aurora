"""
Base FastAPI application template for Aurora microservices
Usa configuración unificada desde shared/settings.py
"""
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid

from .aurora_logging import setup_logging, log_request
from .settings import get_service_config, Service, ServiceConfig


class BaseService:
    """Base class for Aurora microservices (refactorizada para usar settings globales)"""

    def __init__(
        self,
        service: Service,
        title: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "1.0.0",
    ):
        # === Configuración desde .env ===
        self.config: ServiceConfig = get_service_config(service)
        self.service_name = self.config.service_name

        # === Logging ===
        self.logger = setup_logging(
            service_name=self.service_name,
            level=self.config.log_level,
            use_json=self.config.environment != "development"
        )

        # === Ciclo de vida del servicio ===
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            self.logger.info(f"🚀 Starting {self.service_name}")
            yield
            self.logger.info(f"🛑 Shutting down {self.service_name}")

        # === FastAPI App ===
        self.app = FastAPI(
            title=title or f"{self.service_name.title()}",
            description=description or f"Aurora {self.service_name} microservice",
            version=version,
            lifespan=lifespan,
        )

        # Inicialización
        self._setup_middleware()
        self._setup_exception_handlers()
        self._setup_health_endpoints()

    # ---------- Middleware ----------
    def _setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
            request.state.correlation_id = correlation_id
            start = time.time()

            response = await call_next(request)

            response.headers["X-Correlation-ID"] = correlation_id
            process_time = (time.time() - start) * 1000

            log_request(
                logger=self.logger,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                response_time_ms=process_time,
                correlation_id=correlation_id,
                user_agent=request.headers.get("User-Agent"),
                ip_address=request.client.host if request.client else None,
            )
            return response

    # ---------- Exception Handlers ----------
    def _setup_exception_handlers(self):
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
            self.logger.error(
                f"HTTP error: {exc.detail}",
                extra={"correlation_id": correlation_id, "status_code": exc.status_code},
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error_code": "HTTP_ERROR",
                    "error_message": str(exc.detail),
                    "correlation_id": correlation_id,
                    "timestamp": time.time(),
                    "service_name": self.service_name,
                },
            )

        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
            self.logger.error(
                f"Unhandled exception: {exc}",
                extra={"correlation_id": correlation_id, "exception_type": type(exc).__name__},
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "error_message": "An internal server error occurred",
                    "correlation_id": correlation_id,
                    "timestamp": time.time(),
                    "service_name": self.service_name,
                },
            )

    # ---------- Health Endpoints ----------
    def _setup_health_endpoints(self):
        @self.app.get("/health/live")
        async def liveness_check():
            return {
                "status": "alive",
                "service": self.service_name,
                "timestamp": time.time(),
            }

        @self.app.get("/health/ready")
        async def readiness_check():
            return {
                "status": "ready",
                "service": self.service_name,
                "timestamp": time.time(),
            }

    # ---------- Utilities ----------
    def add_router(self, router, prefix: str = "", tags: Optional[List[str]] = None):
        self.app.include_router(router, prefix=prefix, tags=tags)

    def get_correlation_id_dependency(self):
        def get_correlation_id(request: Request) -> str:
            return getattr(request.state, "correlation_id", str(uuid.uuid4()))
        return get_correlation_id