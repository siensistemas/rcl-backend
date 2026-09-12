from .base import *

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Reverse proxy (Nginx reverse proxy for www.siensistemas.com/rcl/)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Served under a subpath (e.g. www.siensistemas.com/rcl/)
FORCE_SCRIPT_NAME = env('SCRIPT_NAME', default='')
if FORCE_SCRIPT_NAME and FORCE_SCRIPT_NAME.endswith('/'):
    FORCE_SCRIPT_NAME = FORCE_SCRIPT_NAME.rstrip('/')

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://www.siensistemas.com',
])

# Add reverse-proxy aware IP middleware for production
if 'shared.proxymiddleware.RealIPMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(0, 'shared.proxymiddleware.RealIPMiddleware')

# Static files with S3
if env.bool('USE_S3', default=False):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_DEFAULT_ACL = env('AWS_DEFAULT_ACL', default='public-read')
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False

# Logging
LOGGING['handlers']['file']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
