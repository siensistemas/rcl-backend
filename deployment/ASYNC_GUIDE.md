# Guia de Funciones Asincronas (Celery + Redis)

Backend: `core/celery.py` con `autodiscover_tasks()` activo.
Worker y beat ya corren en Docker Compose (dev y prod).

---

## 1. Crear una tarea simple

En cualquier app, crear `tasks.py`:

```python
# apps/users/tasks.py
from celery import shared_task

@shared_task
def enviar_email_verificacion(user_id, code):
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from .models import User

    user = User.objects.get(id=user_id)
    html = render_to_string('emails/verification.html', {
        'user': user,
        'code': code,
    })
    send_mail(
        subject='Verifica tu email - RCL',
        message='Código: ' + code,
        html_message=html,
        recipient_list=[user.email],
    )
```

Requisitos:
- Archivo se llama `tasks.py` y está dentro de una app registrada en `INSTALLED_APPS`.
- `autodiscover_tasks()` en `core/celery.py` lo detecta automáticamente.
- Usar `@shared_task` (no `@app.task`) para que funcione sin importar la app Celery.
- Tareas importan modelos dentro del body (`from .models import ...`) para evitar circular imports.

---

## 2. Invocar desde un servicio o view

```python
from apps.users.tasks import enviar_email_verificacion

# Ejecucion asincrona (no bloquea el request)
enviar_email_verificacion.delay(user.id, code)

# Con argumentos keyword
enviar_email_verificacion.apply_async(
    args=[user.id, code],
    countdown=5,  # esperar 5 segundos antes de ejecutar
)
```

`.delay()` es equivalente a `.apply_async(args=[...])` pero con menos opciones.
El worker de Celery lo recoge y ejecuta en otro proceso.

---

## 3. Tareas periodicas (Celery Beat)

### Opcion A: CELERY_BEAT_SCHEDULE (config estatica)

En `core/settings/base.py`:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'expirar-promociones-cada-dia': {
        'task': 'apps.promotions.tasks.expirar_promociones',
        'schedule': crontab(hour=0, minute=0),  # medianoche
    },
    'limpiar-codigos-expirados': {
        'task': 'apps.users.tasks.limpiar_codigos_verificacion',
        'schedule': crontab(hour=3, minute=0),  # 3am
    },
}
```

### Opcion B: django-celery-beat (tabla en la BD)

Permite crear/editar tareas periodicas desde el admin Django (`/admin/django_celery_beat/`).
No requiere reiniciar el servicio `celery-beat`.

Crear el schedule en admin o via codigo:

```python
from django_celery_beat.models import PeriodicTask, CrontabSchedule

schedule, _ = CrontabSchedule.objects.get_or_create(
    hour=0, minute=0, day_of_week='*'
)
PeriodicTask.objects.get_or_create(
    name='expirar-promociones-daily',
    task='apps.promotions.tasks.expirar_promociones',
    crontab=schedule,
)
```

---

## 4. Ejemplo completo: crear tabla tasks + primera tarea

En `apps/promotions/tasks.py`:

```python
from celery import shared_task
from django.utils import timezone

@shared_task
def expirar_promociones():
    from .models import Promotion

    now = timezone.now()
    actualizadas = Promotion.objects.filter(
        status='active',
        end_date__lt=now,
    ).update(status='expired')

    return f'{actualizadas} promociones expiradas'
```

---

## 5. Configuracion (ya aplicada en este proyecto)

```python
# core/settings/base.py
CELERY_BROKER_URL      = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND   = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT   = ['json']
CELERY_TASK_SERIALIZER  = 'json'
CELERY_RESULT_SERIALIZER= 'json'
CELERY_TIMEZONE         = 'America/Bogota'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT  = 30 * 60  # 30 min max
```

Redis como broker: `REDIS_URL=redis://redis:6379/0` en docker, `redis://localhost:6379/0` en local.

---

## 6. Probar en desarrollo

```bash
# Terminal 1: worker
celery -A core worker --loglevel=info

# Terminal 2: beat (opcional, solo si hay tareas periodicas)
celery -A core beat --loglevel=info

# Django shell
python manage.py shell
>>> from apps.users.tasks import enviar_email_verificacion
>>> enviar_email_verificacion.delay(1, '123456')
<AsyncResult: ...>
```

En Docker Compose (ya levantado):

```bash
docker compose logs celery     # ver ejecucion de tareas
docker compose logs celery-beat
```

---

## 7. Enviar archivos/grandes con tareas

```python
@shared_task
def generar_reporte(usuario_id):
    # genera CSV/PDF, lo guarda en MEDIA_ROOT
    ...
    return '/media/reportes/enero.csv'
```

Desde el view:
```python
@action(detail=False, methods=['post'])
def descargar_reporte(self, request):
    task = generar_reporte.delay(request.user.id)
    return Response({'task_id': str(task.id)})
```

---

## 8. Ver estado de una tarea

```python
from celery.result import AsyncResult

result = AsyncResult('task-id-aqui')
result.status   # PENDING, STARTED, SUCCESS, FAILURE, RETRY
result.ready()  # True si termino
result.get()    # resultado (bloquea hasta que termine)
result.info     # info de progreso
```

---

## 9. Cuidados en produccion

- **No pasar objetos grandes** por `args=`. Pasar IDs y buscar dentro de la tarea.
- **Usar `countdown` o `eta`** para no sobrecargar el broker en picos.
- **Manejar errores** con `autoretry_for=(Exception,), retry_backoff=True`.
- **Timeout**: `CELERY_TASK_TIME_LIMIT` ya esta en 30 min.
- **Resultados**: si no se necesitan resultados, pasar `ignore_result=True`.
- **Seguridad**: las tareas se ejecutan en el worker; no ejecutar codigo arbitrario del request.

---

## 10. Casos de uso tipicos para este proyecto

| Caso | Tarea | Frecuencia |
|------|-------|-----------|
| Email de verificacion | `enviar_email_verificacion` | por registro |
| Email de bienvenida | `enviar_email_bienvenida` | por registro |
| Expirar promociones | `expirar_promociones` | diaria (beat) |
| Notificaciones push | `enviar_notificacion_push` | por evento |
| Reportes/analitica | `generar_reporte` | manual |
| Limpiar tokens expirados | `limpiar_tokens_expirados` | semanal (beat) |
| Recordatorios a comerciantes | `enviar_recordatorio_suscripcion` | semanal (beat) |