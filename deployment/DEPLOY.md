# Guia de Despliegue - RCL Backend
## Servidor casero - Linux + Docker Compose + Nginx

Backend queda publicado en: **https://www.siensistemas.com/rcl/**

### Requisitos del servidor
- Linux (Debian/Ubuntu recomendado)
- Docker + Docker Compose
- Nginx
- Dominio apuntando a tu IP (Cloudflare con proxy)

---

## 1. Instalar Docker y Nginx en el servidor

```bash
# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Docker Compose plugin
sudo apt-get update
sudo apt-get install -y docker-compose-plugin nginx

# Certbot para SSL (si no usas full-strict de Cloudflare)
sudo apt-get install -y certbot python3-certbot-nginx
```

## 2. Clonar / subir el proyecto

```bash
sudo mkdir -p /opt/rcl-backend
cd /opt/rcl-backend
# Copiar el contenido del repo aqui, o clonar
git clone <tu-repo> .
```

## 3. Configurar variables de entorno (.env)

```bash
cp .env.production.example .env
nano .env
```
- Cambia `SECRET_KEY`, `DB_PASSWORD` y `ADMIN_PASSWORD` por valores fuertes unicos.
- `SCRIPT_NAME=/rcl` ya esta seteado.
- Si Cloudflare usa "Full (strict)", deja `EMAIL_*` segun tu SMTP.

## 4. Creamos carpetas para static/media y permisos

```bash
sudo mkdir -p /opt/rcl-backend/static /opt/rcl-backend/media
sudo chown -R $USER:$USER /opt/rcl-backend/static /opt/rcl-backend/media
```

## 5. Levantar con Docker Compose (produccion)

```bash
cd /opt/rcl-backend
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps   # ver estado
docker compose -f docker-compose.prod.yml logs backend
```

Se habilitan: db (PostGIS) + redis + backend (gunicorn :8000 solo localhost) + celery + celery-beat.

## 6. Configurar Nginx

```bash
sudo cp deployment/nginx-rcl.conf /etc/nginx/sites-available/rcl
sudo ln -s /etc/nginx/sites-available/rcl /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

En el archivo se asume `/opt/rcl-backend/static` y `/opt/rcl-backend/media`.

## 7. SSL con Let's Encrypt

```bash
sudo certbot --nginx -d www.siensistemas.com
```
Si Cloudflare esta con proxy activo y "Full (strict)", debemos emitir el certificado en el servidor y copiar rutas en el conf, o desactivar temporalmente el proxy de Cloudflare al emitir.

## 8. Verificar

- API docs: https://www.siensistemas.com/rcl/swagger/
- ReDoc: https://www.siensistemas.com/rcl/redoc/
- Admin Django: https://www.siensistemas.com/rcl/admin/
- Endpoint de salud: https://www.siensistemas.com/rcl/api/v1/auth/me/

## Backup (recomendado)

```bash
# Base de datos
docker compose -f docker-compose.prod.yml exec db pg_dump -U rcl_user rcl_db > backup_rcl.sql

# Media
tar czf media_backup.tar.gz /opt/rcl-backend/media
```

## Actualizaciones

```bash
cd /opt/rcl-backend
git pull
docker compose -f docker-compose.prod.yml up -d --build
```
