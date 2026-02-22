"""
Development settings — SQLite, debug on, verbose logging.
"""
import sys
from .base import *  # noqa

DEBUG = True


TESTING = "test" in sys.argv

if TESTING:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Show emails in console during development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
