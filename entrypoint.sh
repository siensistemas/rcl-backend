#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 1
done
echo "PostgreSQL started"

# Solo el servicio backend ejecuta inicializacion (migraciones, static, superuser).
# Los workers (celery/celery-beat) deben levantarse sin tocar la base de datos.
if [ "${RUN_INIT}" = "1" ]; then
  echo "Running migrations..."
  python manage.py migrate

  echo "Collecting static files..."
  python manage.py collectstatic --noinput

  echo "Creating superuser if missing..."
  python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('ADMIN_USERNAME', 'admin')
email = os.environ.get('ADMIN_EMAIL', 'admin@siensistemas.com')
password = os.environ.get('ADMIN_PASSWORD', 'admin123')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print('Superuser created')
else:
    print('Superuser already exists')
"
else
  echo "RUN_INIT not set - skipping initialization"
fi

echo "Starting server..."
exec "$@"