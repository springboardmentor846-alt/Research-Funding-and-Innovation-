"""
Project Constants Specification
"""

from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class UserRole(str, Enum):
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    RESEARCHER = "RESEARCHER"
    STARTUP_FOUNDER = "STARTUP_FOUNDER"
    INNOVATION_MANAGER = "INNOVATION_MANAGER"
    OSP_ADMIN = "OSP_ADMIN"
    REVIEWER = "REVIEWER"


class TenantTier(str, Enum):
    FREE_TRIAL = "FREE_TRIAL"
    STANDARD = "STANDARD"
    ENTERPRISE = "ENTERPRISE"
    GOVERNMENT = "GOVERNMENT"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


# API Versioning & Routing Constants
API_V1_STR: str = "/api/v1"
HEALTH_CHECK_PATH: str = "/health"

# Security & Token Expiration Defaults
ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
REFRESH_TOKEN_EXPIRE_DAYS: int = 7
ALGORITHM: str = "HS256"
