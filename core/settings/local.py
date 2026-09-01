from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Database - PostgreSQL local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='busca_me_db'),
        'USER': env('DB_USER', default='busca_me_user'),
        'PASSWORD': env('DB_PASSWORD', default='busca_me_password'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# Email for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS for development
CORS_ALLOW_ALL_ORIGINS = True

# Disable throttling
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []