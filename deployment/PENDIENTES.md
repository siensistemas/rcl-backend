# Pendientes - RCL Backend

## [2026-09-18] Configurar SMTP en produccion
- **Registrado:** 2026-09-13
- **Origen:** Despliegue nativo gunicorn/systemd en `/home/django_siensistemas/rcl_backend`
- **Tarea:** Editar `/home/django_siensistemas/rcl_backend/.env` y llenar:
  ```
  EMAIL_HOST=smtp.gmail.com
  EMAIL_PORT=587
  EMAIL_HOST_USER=<email remitente>
  EMAIL_HOST_PASSWORD=<app password>
  EMAIL_USE_TLS=True
  ```
- Luego: `sudo systemctl restart gunicorn-rcl`
- Alternativa: Mailgun/SendGrid en lugar de Gmail.
- Estado: PENDIENTE