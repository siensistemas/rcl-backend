# Guia de Despliegue - Busca Me Backend
## Servidor casero - Linux + Docker Compose + Nginx

Backend queda publicado en: **https://www.siensistemas.com/busca_me/**

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
sudo mkdir -p /opt/busca-me-backend
cd /opt/busca-me-backend
# Copiar el contenido del repo aqui, o clonar
git clone <tu-repo> .
```

## 3. Configurar variables de entorno (.env)

```bash
cp .env.production.example .env
nano .env
```
- Cambia `SECRET_KEY`, `DB_PASSWORD` y `ADMIN_PASSWORD` por valores fuertes unicos.
- `SCRIPT_NAME=/busca_me` ya esta seteado.
- Si Cloudflare usa "Full (strict)", deja `EMAIL_*` segun tu SMTP.

## 4. Creamos carpetas para static/media y permisos

```bash
sudo mkdir -p /opt/busca-me-backend/static /opt/busca-me-backend/media
sudo chown -R $USER:$USER /opt/busca-me-backend/static /opt/busca-me-backend/media
```

## 5. Levantar con Docker Compose (produccion)

```bash
cd /opt/busca-me-backend
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps   # ver estado
docker compose -f docker-compose.prod.yml logs backend
```

Se habilitan: db (PostGIS) + redis + backend (gunicorn :8000 solo localhost) + celery + celery-beat.

## 6. Configurar Nginx

```bash
sudo cp deployment/nginx-busca-me.conf /etc/nginx/sites-available/busca-me
sudo ln -s /etc/nginx/sites-available/busca-me /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

En el archivo se asume `/opt/busca-me-backend/static` y `/opt/busca-me-backend/media`.

## 7. SSL con Let's Encrypt

```bash
sudo certbot --nginx -d www.siensistemas.com
```
Si Cloudflare esta con proxy activo y "Full (strict)", debemos emitir el certificado en el servidor y copiar rutas en el conf, o desactivar temporalmente el proxy de Cloudflare al emitir.

## 8. Verificar

- API docs: https://www.siensistemas.com/busca_me/swagger/
- ReDoc: https://www.siensistemas.com/busca_me/redoc/
- Admin Django: https://www.siensistemas.com/busca_me/admin/
- Endpoint de salud: https://www.siensistemas.com/busca_me/api/v1/auth/me/

## Backup (recomendado)

```bash
# Base de datos
docker compose -f docker-compose.prod.yml exec db pg_dump -U busca_me_user busca_me_db > backup_busca_me.sql

# Media
tar czf media_backup.tar.gz /opt/busca-me-backend/media
```

## Actualizaciones

```bash
cd /opt/busca-me-backend
git pull
docker compose -f docker-compose.prod.yml up -d --build
```