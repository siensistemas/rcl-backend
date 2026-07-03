from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS for development
CORS_ALLOW_ALL_ORIGINS = True

# Disable throttling
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
