import logging
import sys
from app.core.config import settings
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

def setup_logging():
    # Create logger
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Setup logging when imported
logger = setup_logging()
