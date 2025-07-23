"""Superset configuration for local development."""

import os
from typing import Any, Dict

# Superset Configuration
import os

# Database configuration
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/ads_campaign')

# Secret key for session management
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'your-secret-key-here')

# Enable feature flags
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_RBAC': True,
}

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
}

# Security configuration
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# Logging configuration
ENABLE_TIME_ROTATE = True
TIME_ROTATE_LOG_LEVEL = 'DEBUG'
FILENAME = os.path.join(os.path.dirname(__file__), 'superset.log')

# Row limit for queries
ROW_LIMIT = 5000
VIZ_ROW_LIMIT = 10000

# Enable SQL Lab
ENABLE_PROXY_FIX = True
ENABLE_TEMPLATE_PROCESSING = True 