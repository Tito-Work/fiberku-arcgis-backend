"""
Request/Response Logging Middleware
Middleware untuk logging request body dan response body dengan correlation ID
"""

import json
import time
from typing import Dict, Any, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logging_system import app_logger, get_correlation_id, log_request_start, log_request_end


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware untuk logging request dan response dengan correlation ID"""
    
    def __init__(self, app):
        super().__init__(app)
        self.max_body_size = 1024 * 1024  # 1MB limit untuk body logging
        
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = get_correlation_id()
        
        # Log request start
        request_body = await self._get_request_body(request)

        correlation_id = log_request_start(
            app_logger,
            method=request.method,
            path=str(request.url.path),
            client_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            content_type=request.headers.get("content-type", ""),
            request_body=request_body
        )
        
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = (time.time() - start_time) * 1000
            
            # Log response
            response_body = await self._get_response_body(response)
            log_request_end(
                app_logger,
                correlation_id=correlation_id,
                status_code=response.status_code,
                duration=duration,
                response_body=response_body,
                response_headers=dict(response.headers)
            )
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = (time.time() - start_time) * 1000
            
            # Log error
            app_logger.error(
                f"Request failed: {str(e)}",
                correlation_id=correlation_id,
                event="request_error",
                method=request.method,
                path=str(request.url.path),
                duration=duration,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
    
    async def _get_request_body(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract request body safely"""
        try:
            # Skip logging for certain endpoints
            if self._should_skip_logging(request):
                return None
                
            # Check content type
            content_type = request.headers.get("content-type", "")
            if "application/json" not in content_type:
                return None
                
            # Read request body
            body_bytes = await request.body()
            if not body_bytes:
                return None
                
            # Limit body size
            if len(body_bytes) > self.max_body_size:
                return {"error": "Body too large to log", "size": len(body_bytes)}
                
            # Parse JSON
            body_json = json.loads(body_bytes.decode('utf-8'))
            
            # Sensitive data masking
            return self._mask_sensitive_data(body_json)
            
        except Exception as e:
            app_logger.warning(f"Failed to parse request body: {str(e)}")
            return {"error": "Failed to parse request body"}
    
    async def _get_response_body(self, response: Response) -> Optional[Dict[str, Any]]:
        """Extract response body safely"""
        try:
            # Skip logging for non-JSON responses
            if not isinstance(response, JSONResponse):
                return None
                
            # Check response body size
            body_bytes = response.body
            if not body_bytes:
                return None
                
            # Limit body size
            if len(body_bytes) > self.max_body_size:
                return {"error": "Response body too large", "size": len(body_bytes)}
                
            # Parse JSON
            body_json = json.loads(body_bytes.decode('utf-8'))
            
            # Sensitive data masking
            return self._mask_sensitive_data(body_json)
            
        except Exception as e:
            app_logger.warning(f"Failed to parse response body: {str(e)}")
            return {"error": "Failed to parse response body"}
    
    def _should_skip_logging(self, request: Request) -> bool:
        """Skip logging untuk endpoint tertentu"""
        skip_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/favicon.ico"
        ]
        
        # Skip untuk path tertentu
        if any(request.url.path.startswith(path) for path in skip_paths):
            return True
            
        # Skip untuk method GET biasa (kecuali jika ada query parameters)
        if request.method == "GET" and not request.query_params:
            return True
            
        return False
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data di request/response body"""
        if not isinstance(data, dict):
            return data
            
        sensitive_fields = [
            "password",
            "password_confirmation",
            "token",
            "secret",
            "api_key",
            "authorization",
            "credit_card",
            "cvv",
            "card_number"
        ]
        
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                masked_data[key] = "*****MASKED*****"
            elif isinstance(value, dict):
                masked_data[key] = self._mask_sensitive_data(value)
            elif isinstance(value, list):
                masked_data[key] = [
                    self._mask_sensitive_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
        
        return masked_data