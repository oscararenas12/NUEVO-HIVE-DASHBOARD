"""Shared rate limiter (SEC-004).

A single module-level Limiter so route decorators and the app share one instance.
Enabled state comes from config; the test suite sets RATE_LIMIT_ENABLED=false.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import get_settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=get_settings().rate_limit_enabled,
)
