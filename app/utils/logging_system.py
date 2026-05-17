"""
Advanced Logging System with Grafana Integration
Structured logging with correlation IDs, request tracing, and monitoring support
"""

import logging
import sys
import uuid
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import contextmanager
from app.core.config import settings
from pathlib import Path


class StructuredLogger:
    """Advanced structured logger with correlation tracking"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create file handler for persistent logs only
        # Get project root directory (go up from app/utils to project root)
        project_root = Path(__file__).resolve().parent.parent.parent
        log_file = project_root / 'logs' / 'app.log'
        
        # Ensure logs directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        formatter = StructuredFormatter()

        # app.log - semua log
        app_file_handler = logging.FileHandler(log_file)
        app_file_handler.setLevel(logging.INFO)
        app_file_handler.setFormatter(formatter)
        self.logger.addHandler(app_file_handler)

        # error.log - hanya ERROR ke atas
        error_log_file = project_root / 'logs' / 'error.log'
        error_file_handler = logging.FileHandler(error_log_file)
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        self.logger.addHandler(error_file_handler)
        
            
    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data"""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        self.logger.debug(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with structured data"""
        self.logger.critical(message, extra=kwargs)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with correlation IDs"""
    
    def format(self, record):
        """Format log record with structured data"""
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            log_entry['correlation_id'] = record.correlation_id
        
        # Add only custom extra fields from record
        reserved_keys = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "taskName", "message"
        }

        for key, value in record.__dict__.items():
            if key not in reserved_keys and key not in log_entry:
                log_entry[key] = value
        
        # Add request context if available
        if hasattr(record, 'request_context'):
            log_entry['request_context'] = record.request_context
        
        # Add user context if available
        if hasattr(record, 'user_context'):
            log_entry['user_context'] = record.user_context
        
        # Add performance metrics if available
        if hasattr(record, 'performance'):
            log_entry['performance'] = record.performance
        
        # Return JSON formatted log
        return json.dumps(log_entry, default=str)


def get_correlation_id() -> str:
    """Generate or get correlation ID for request tracing"""
    return str(uuid.uuid4())


def log_request_start(logger: StructuredLogger, method: str, path: str, **kwargs):
    """Log request start with correlation ID"""

    correlation_id = kwargs.pop("correlation_id", None) or get_correlation_id()

    logger.info(
        f"Request started: {method} {path}",
        correlation_id=correlation_id,
        event="request_start",
        method=method,
        path=path,
        **kwargs
    )

    return correlation_id


def log_request_end(logger: StructuredLogger, correlation_id: str = None, status_code: int = 200, **kwargs):
    """Log request end with correlation ID"""

    correlation_id = kwargs.pop("correlation_id", None) or correlation_id or get_correlation_id()
    duration = kwargs.pop("duration", 0)

    log_data = {
        "correlation_id": correlation_id,
        "event": "request_end",
        "status_code": status_code,
        "duration": duration,
        **kwargs
    }

    message = f"Request completed: status={status_code}, duration={duration}ms"

    if status_code >= 500:
        logger.error(message, **log_data)
    elif status_code >= 400:
        logger.warning(message, **log_data)
    else:
        logger.info(message, **log_data)


def log_performance(logger: StructuredLogger, operation: str, duration: float, **kwargs):
    """Log performance metrics"""
    logger.info(
        f"Performance: {operation} completed in {duration:.2f}ms",
        event="performance",
        operation=operation,
        duration=duration,
        **kwargs
    )


def log_security_event(logger: StructuredLogger, event_type: str, **kwargs):
    """Log security events"""
    logger.warning(
        f"Security event: {event_type}",
        event="security",
        event_type=event_type,
        **kwargs
    )


def log_business_event(logger: StructuredLogger, event_type: str, **kwargs):
    """Log business events"""
    logger.info(
        f"Business event: {event_type}",
        event="business",
        event_type=event_type,
        **kwargs
    )


def log_system_event(logger: StructuredLogger, event_type: str, **kwargs):
    """Log system events"""
    logger.info(
        f"System event: {event_type}",
        event="system",
        event_type=event_type,
        **kwargs
    )


class RequestLogger:
    """Middleware for request logging with correlation tracking"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
    
    def __call__(self, func):
        """Decorator to log function calls"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            correlation_id = get_correlation_id()
            start_time = time.time()
            
            # Log function start
            self.logger.info(
                f"Function call: {func.__name__}",
                correlation_id=correlation_id,
                event="function_start",
                function=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                
                # Log function completion
                self.logger.info(
                    f"Function completed: {func.__name__}",
                    correlation_id=correlation_id,
                    event="function_end",
                    function=func.__name__,
                    duration=duration,
                    success=True
                )
                
                return result
                
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                
                # Log function error
                self.logger.error(
                    f"Function failed: {func.__name__}",
                    correlation_id=correlation_id,
                    event="function_error",
                    function=func.__name__,
                    duration=duration,
                    error=str(e),
                    success=False
                )
                raise
        
        return wrapper


@contextmanager
def log_context(logger: StructuredLogger, context_type: str, **context_data):
    """Context manager for logging with context"""
    correlation_id = get_correlation_id()
    
    logger.info(
        f"Context started: {context_type}",
        correlation_id=correlation_id,
        event="context_start",
        context_type=context_type,
        **context_data
    )
    
    try:
        yield context_data
    finally:
        logger.info(
            f"Context ended: {context_type}",
            correlation_id=correlation_id,
            event="context_end",
            context_type=context_type
        )


def setup_logging():
    """Setup advanced logging configuration"""
    # Configure root logger
    # Get project root directory (go up from app/utils to project root)
    project_root = Path(__file__).resolve().parent.parent.parent
    LOG_DIR = project_root / "logs"

    LOG_DIR.mkdir(exist_ok=True)

    LOG_FILE = LOG_DIR / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.StreamHandler(), logging.FileHandler(LOG_FILE)],
        format='%(message)s'
    )
    
    # Create loggers for different components
    loggers = {
        'app': StructuredLogger('app', 'INFO'),
        'auth': StructuredLogger('auth', 'INFO'),
        'api': StructuredLogger('api', 'INFO'),
        'security': StructuredLogger('security', 'WARNING'),
        'performance': StructuredLogger('performance', 'INFO'),
        'business': StructuredLogger('business', 'INFO'),
        'system': StructuredLogger('system', 'INFO'),
    }
    
    return loggers


def log_errors(logger=None):
    """Decorator to log errors in functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Use provided logger or default app_logger
                error_logger = logger or app_logger
                error_logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    function=func.__name__,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys())
                )
                raise
        return wrapper
    return decorator

# Create default loggers
app_logger = StructuredLogger('app', 'INFO')
auth_logger = StructuredLogger('auth', 'INFO')
api_logger = StructuredLogger('api', 'INFO')
security_logger = StructuredLogger('security', 'WARNING')
performance_logger = StructuredLogger('performance', 'INFO')
business_logger = StructuredLogger('business', 'INFO')
system_logger = StructuredLogger('system', 'INFO')
