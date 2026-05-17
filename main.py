"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.database import engine
from app.routers import auth, users, roles, permissions, customers, packages, coverages, segments, operators, fiber_optics, geojson
from app.models import Base
from app.utils.logging_system import setup_logging, app_logger, log_errors
from app.core.config import settings
from app.exceptions.http_exception import AppException
from app.middleware.logging import RequestResponseLoggingMiddleware
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
setup_logging()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Logging Middleware
app.add_middleware(RequestResponseLoggingMiddleware)  # Add the new middleware

# Exception logging middleware
@app.middleware("http")
async def exception_logging_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        app_logger.error(
            f"Middleware caught exception: {str(e)}",
            exception_type=type(e).__name__,
            error_message=str(e),
            path=str(request.url.path),
            method=request.method,
            status_code=500
        )
        raise

# Include routers
app.include_router(auth.router, prefix=f"{settings.api_v1_str}/auth", tags=["authentication"])
app.include_router(users.router, prefix=f"{settings.api_v1_str}/users", tags=["users"])
app.include_router(roles.router, prefix=f"{settings.api_v1_str}/roles", tags=["roles"])
app.include_router(permissions.router, prefix=f"{settings.api_v1_str}/permissions", tags=["permissions"])

# Network management routers
app.include_router(customers.router, prefix=f"{settings.api_v1_str}/customers", tags=["customers"])
app.include_router(packages.router, prefix=f"{settings.api_v1_str}/packages", tags=["packages"])
app.include_router(coverages.router, prefix=f"{settings.api_v1_str}/coverages", tags=["coverages"])
app.include_router(segments.router, prefix=f"{settings.api_v1_str}/segments", tags=["segments"])
app.include_router(operators.router, prefix=f"{settings.api_v1_str}/operators", tags=["operators"])
app.include_router(fiber_optics.router, prefix=f"{settings.api_v1_str}/fiber-optics", tags=["fiber-optics"])

# GeoJSON routers
app.include_router(geojson.router, prefix=f"{settings.api_v1_str}/geojson", tags=["geojson"])

# Root endpoint
@app.get("/")
@log_errors()
def read_root():
    app_logger.info("Root endpoint accessed")
    return {"message": f"Welcome to {settings.app_name}"}

# Health check
@app.get("/health")
@log_errors()
def health_check():
    return {"status": "healthy", "version": settings.app_version}

# Test error endpoint
@app.get("/test-error")
@log_errors()
def test_error():
    """Test endpoint to trigger error logging"""
    raise Exception("This is a test error to verify logging works")

# HTTPException handler for FastAPI's built-in HTTPException
@app.exception_handler(FastAPIHTTPException)
async def fastapi_http_exception_handler(request: Request, exc: FastAPIHTTPException):
    status_code_str = str(exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "code": status_code_str,
            "message": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            "data": exc.detail if not isinstance(exc.detail, str) else None
        }
    )

# Validation error handler for Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    return JSONResponse(
        status_code=422,
        content={
            "status": False,
            "code": "422",
            "message": "Validation error",
            "data": errors
        }
    )

# SQLAlchemy error handler for database integrity errors
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
    
    # Extract constraint name if available
    detail = ""
    if hasattr(exc, 'orig') and hasattr(exc.orig, 'pgcode'):
        detail = error_message
    
    app_logger.error(
        f"Database error: {error_message}",
        exception_type="SQLAlchemyError",
        error_message=error_message,
        path=str(request.url.path),
        method=request.method,
        status_code=400
    )
    return JSONResponse(
        status_code=400,
        content={
            "status": False,
            "code": "400",
            "message": "Database error: " + error_message,
            "data": None
        }
    )

# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    app_logger.error(
        f"AppException: {exc.message}",
        exception_type="AppException",
        status_code=exc.status_code,
        code=exc.code,
        data=exc.data,
        path=str(request.url.path)
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "code": exc.code,
            "message": exc.message,
            "data": exc.data
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    app_logger.error(
        f"Unhandled exception: {str(exc)}",
        exception_type=type(exc).__name__,
        error_message=str(exc),
        path=str(request.url.path),
        method=request.method,
        status_code=500
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "code": "500",
            "message": "Internal server error",
            "data": None
        }
    )