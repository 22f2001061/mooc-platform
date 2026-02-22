"""
Production settings — PostgreSQL, debug off, security hardened.
"""
import os
from .base import *  # noqa

DEBUG = False

# In production, set SECRET_KEY via environment variable
SECRET_KEY = os.environ["SECRET_KEY"]

# Parse DATABASE_URL: postgres://user:password@host:5432/dbname
DATABASE_URL = os.environ.get("DATABASE_URL", "")

if DATABASE_URL:
    import urllib.parse

    result = urllib.parse.urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": result.path[1:],
            "USER": result.username,
            "PASSWORD": result.password,
            "HOST": result.hostname,
            "PORT": result.port or 5432,
            "CONN_MAX_AGE": 60,  # persistent connections
        }
    }
else:
    raise ValueError("DATABASE_URL must be set in production")

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

STATIC_ROOT = BASE_DIR / "staticfiles"
