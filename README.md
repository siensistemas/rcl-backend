# Busca Me - Backend

Plataforma SaaS Multi-Tenant para comercios locales.

## Tecnologias

- **Backend**: Django 4.2.7 + Django REST Framework
- **Database**: PostgreSQL 15 + PostGIS
- **Cache**: Redis 7
- **Async**: Celery 5
- **Auth**: JWT (djangorestframework-simplejwt)
- **Storage**: S3 Compatible (AWS, Cloudflare R2, Backblaze B2, MinIO)
- **Docs**: Swagger/OpenAPI
- **Container**: Docker + Docker Compose

## Estructura del Proyecto

\\\
busca-me-backend/
â”œâ”€â”€ core/                      # Configuracion principal
â”‚   â”œâ”€â”€ settings/
â”‚   â”‚   â”œâ”€â”€ base.py           # Configuracion base
â”‚   â”‚   â”œâ”€â”€ local.py          # Configuracion desarrollo
â”‚   â”‚   â””â”€â”€ production.py     # Configuracion produccion
â”‚   â”œâ”€â”€ urls.py
â”‚   â”œâ”€â”€ wsgi.py
â”‚   â””â”€â”€ asgi.py
â”œâ”€â”€ apps/                      # Aplicaciones Django
â”‚   â”œâ”€â”€ tenants/              # Multi-tenant (municipios)
â”‚   â”œâ”€â”€ users/                # Usuarios y autenticacion
â”‚   â”œâ”€â”€ categories/           # Categorias ilimitadas
â”‚   â”œâ”€â”€ businesses/           # Comercios
â”‚   â”œâ”€â”€ promotions/           # Promociones
â”‚   â”œâ”€â”€ subscriptions/        # Planes y suscripciones
â”‚   â”œâ”€â”€ events/               # Eventos
â”‚   â”œâ”€â”€ tourism/              # Turismo
â”‚   â”œâ”€â”€ jobs/                 # Bolsa de empleo
â”‚   â”œâ”€â”€ classifieds/          # Clasificados
â”‚   â”œâ”€â”€ ratings/              # Calificaciones
â”‚   â”œâ”€â”€ notifications/        # Notificaciones push
â”‚   â”œâ”€â”€ coupons/              # Cupones digitales
â”‚   â”œâ”€â”€ reels/                # Reels y videos cortos
â”‚   â””â”€â”€ analytics/            # Analitica y estadisticas
â”œâ”€â”€ shared/                    # Codigo compartido
â”‚   â”œâ”€â”€ exceptions.py         # Manejo de errores
â”‚   â”œâ”€â”€ permissions.py        # Permisos personalizados
â”‚   â”œâ”€â”€ pagination.py         # Paginacion
â”‚   â”œâ”€â”€ validators.py         # Validadores
â”‚   â””â”€â”€ utils.py              # Utilidades
â”œâ”€â”€ static/                    # Archivos estaticos
â”œâ”€â”€ media/                     # Archivos subidos
â”œâ”€â”€ logs/                      # Logs
â”œâ”€â”€ tests/                     # Pruebas
â”‚   â”œâ”€â”€ unit/
â”‚   â””â”€â”€ integration/
â”œâ”€â”€ docker/                    # Configuracion Docker
â”œâ”€â”€ deployment/                # Configuracion despliegue
â”œâ”€â”€ requirements.txt          # Dependencias
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ docker-compose.yml
â””â”€â”€ manage.py
\\\

## Instalacion

### 1. Clonar y configurar

\\\ash
git clone <repo>
cd busca-me-backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones
\\\

### 2. Base de datos

\\\ash
# Crear base de datos PostgreSQL
createdb -U postgres busca_me_db

# Migrar
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
\\\

### 3. Ejecutar

\\\ash
python manage.py runserver
\\\

### 4. Docker

\\\ash
docker-compose up -d
\\\

## Documentacion API

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/
- OpenAPI Schema: http://localhost:8000/swagger.json

## Despliegue

Produccion (https://www.siensistemas.com/busca_me/): ver [deployment/DEPLOY.md](deployment/DEPLOY.md)

## Endpoints Principales

### Autenticacion
- POST /api/v1/auth/register/ - Registro
- POST /api/v1/auth/login/ - Login
- POST /api/v1/auth/refresh/ - Refresh Token
- POST /api/v1/auth/logout/ - Logout
- GET /api/v1/auth/me/ - Perfil

### Municipios
- GET /api/v1/tenants/municipalities/ - Listar
- POST /api/v1/tenants/municipalities/ - Crear
- GET /api/v1/tenants/municipalities/{id}/ - Detalle

### Categorias
- GET /api/v1/categories/ - Listar
- POST /api/v1/categories/ - Crear

### Comercios
- GET /api/v1/businesses/ - Listar
- POST /api/v1/businesses/ - Crear
- GET /api/v1/businesses/my-businesses/ - Mis comercios
- GET /api/v1/businesses/nearby/ - Cercanos

### Promociones
- GET /api/v1/promotions/ - Listar
- POST /api/v1/promotions/ - Crear
- GET /api/v1/promotions/active/ - Activas
- GET /api/v1/promotions/featured/ - Destacadas

### Suscripciones
- GET /api/v1/subscriptions/plans/ - Planes
- POST /api/v1/subscriptions/subscriptions/ - Suscribirse

## Modelo de Datos

### Core Entities
- Municipality (Tenant)
- User (Usuario)
- Category (Categoria)
- Business (Comercio)
- Promotion (Promocion)
- Plan (Plan)
- Subscription (Suscripcion)

### Relaciones
- Municipality 1---* User
- Municipality 1---* Business
- Municipality 1---* Category
- Business 1---* Promotion
- Business 1---* Subscription
- User 1---* Business (owner)

## Multi-Tenant

La plataforma es Multi-Tenant por defecto:
- Cada municipio es un tenant independiente
- Datos aislados por municipio
- Branding personalizado (logo, colores, etc.)
- Configuracion independiente

## Escalabilidad

- Cache con Redis
- Colas con Celery
- Balanceo de carga
- CDN para archivos estaticos
- Base de datos replicada
- Microservicios (futuro)

## Seguridad

- JWT con refresh tokens
- Rate limiting
- CORS configurado
- Proteccion XSS/SQL Injection
- Logs de auditoria
- Roles y permisos
- Validacion de datos

## Licencia

MIT License
