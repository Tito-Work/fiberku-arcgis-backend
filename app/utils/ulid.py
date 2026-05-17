"""
ULID (Universally Unique Lexicographically Sortable Identifier) utilities
"""

import ulid
from sqlalchemy.types import TypeDecorator, String
from typing import Any
import sqlalchemy as sa

class ULIDType(TypeDecorator):
    """
    SQLAlchemy custom type for ULID
    """
    impl = sa.CHAR(26)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)


def validate_ulid_format(value: str) -> bool:
    """Validate ULID format"""
    if not isinstance(value, str):
        return False
    if len(value) != 26:
        return False
    try:
        ulid.from_str(value)
        return True
    except (ValueError, AttributeError):
        return False


def validate_ulid(value: Any) -> bool:
    """Validate if value is a valid ULID"""
    if isinstance(value, str):
        return validate_ulid_format(value)
    elif isinstance(value, ulid.ULID):
        return True
    else:
        return False


def generate_ulid() -> str:
    """Generate a new ULID as string (lowercase)"""
    return str(ulid.new()).lower()


def parse_ulid(ulid_str: str) -> ulid.ULID:
    """Parse string to ULID object"""
    if not validate_ulid_format(ulid_str):
        raise ValueError(f"Invalid ULID: {ulid_str}")
    return ulid.from_str(ulid_str)
