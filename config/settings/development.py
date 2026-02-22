"""
Development settings — SQLite, debug on, verbose logging.
"""
from .base import *  # noqa

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Show emails in console during development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
