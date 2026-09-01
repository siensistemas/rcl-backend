import os

# Seleccion de configuracion por entorno:
#   DJANGO_ENV=production -> solo settings de produccion (PostgreSQL, S3, SSL...)
#   DJANGO_ENV=local (default) -> solo settings de desarrollo (SQLite, consola, etc.)
# Nunca mezclar ambos bloques: local.py sobrescribe DATABASES/EMAIL/CORS y
# production.py no lo revierte, por lo que fusionar rompe produccion.

DJANGO_ENV = os.environ.get('DJANGO_ENV', 'local')

if DJANGO_ENV == 'production':
    from .production import *
else:
    from .local import *