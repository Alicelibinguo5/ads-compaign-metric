"""Superset configuration for local development."""

import os
from typing import Any, Dict

# Flask App Builder configuration
APP_NAME = "Ads Campaign Metrics Dashboard"
APP_ICON = "/static/assets/images/superset-logo-horiz.png"
FAVICONS = [{"href": "/static/assets/images/favicon.png"}]

# Database configuration
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@postgres:5432/ads_campaign"
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Security
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "your-secret-key-here")

# Feature flags
FEATURE_FLAGS: Dict[str, Any] = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_RBAC": True,
    "ENABLE_EXPLORE_JSON_CSRF_PROTECTION": False,
    "ENABLE_EXPLORE_DRAG_AND_DROP": True,
    "ENABLE_DASHBOARD_NATIVE_FILTERS_SET": True,
    "GLOBAL_ASYNC_QUERIES": True,
    "VERSIONED_EXPORT": True,
    "DASHBOARD_FILTERS_EXPERIMENTAL": True,
}

# Cache configuration
CACHE_CONFIG: Dict[str, Any] = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
}

# Celery configuration (optional for async queries)
class CeleryConfig:
    broker_url = "redis://localhost:6379/0"
    imports = ("superset.sql_lab", "superset.tasks")
    result_backend = "redis://localhost:6379/0"
    worker_prefetch_multiplier = 1
    task_acks_late = False

CELERY_CONFIG = CeleryConfig

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"

# Time grain definitions
TIME_GRAIN_FUNCTIONS = {
    "PT1S": "DATE_TRUNC('second', {col})",
    "PT1M": "DATE_TRUNC('minute', {col})",
    "PT1H": "DATE_TRUNC('hour', {col})",
    "P1D": "DATE_TRUNC('day', {col})",
    "P1W": "DATE_TRUNC('week', {col})",
    "P1M": "DATE_TRUNC('month', {col})",
    "P1Y": "DATE_TRUNC('year', {col})",
}

# Custom CSS
CUSTOM_CSS = """
/* Custom styles for Ads Campaign Metrics Dashboard */
.dashboard-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
"""

# Row limit
ROW_LIMIT = 5000
VIZ_ROW_LIMIT = 10000

# Enable proxy fix
ENABLE_PROXY_FIX = True
PROXY_FIX_CONFIG = {
    "x_for": 1,
    "x_proto": 1,
    "x_host": 1,
    "x_port": 1,
    "x_prefix": 1,
} 