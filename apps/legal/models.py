from django.db import models
from apps.users.models import User


class ConsentRecord(models.Model):
    PURPOSE_CHOICES = (
        ('profile', 'Datos de perfil'),
        ('location', 'Ubicacion'),
        ('push', 'Notificaciones push'),
        ('analytics', 'Analitica de uso'),
        ('ads', 'Publicidad personalizada'),
    )
    MECHANISM_CHOICES = (
        ('first_run_consent_screen', 'Primer inicio - pantalla de consentimiento'),
        ('settings', 'Configuracion de privacidad'),
        ('revoke', 'Revocacion'),
        ('other', 'Otro'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consent_records',
    )
    purpose = models.CharField('Proposito', max_length=20, choices=PURPOSE_CHOICES)
    granted = models.BooleanField('Otorgado', default=True)
    consent_version = models.CharField('Version', max_length=20, default='v1')
    mechanism = models.CharField('Mecanismo', max_length=50, choices=MECHANISM_CHOICES, default='other')
    timestamp = models.DateTimeField('Fecha', auto_now_add=True)
    revoked_at = models.DateTimeField('Revocado', null=True, blank=True)

    class Meta:
        verbose_name = 'Registro de consentimiento'
        verbose_name_plural = 'Registros de consentimiento'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.purpose} ({'OK' if self.granted else 'NO'})"


class RightsRequest(models.Model):
    RIGHT_CHOICES = (
        ('Acceso', 'Acceso'),
        ('Corrección', 'Correccion'),
        ('Portabilidad', 'Portabilidad'),
        ('Oposición', 'Oposicion'),
        ('Limitación del tratamiento', 'Limitacion del tratamiento'),
        ('Eliminación', 'Eliminacion'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('done', 'Completado'),
        ('rejected', 'Rechazado'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rights_requests',
    )
    right = models.CharField('Derecho', max_length=40, choices=RIGHT_CHOICES)
    details = models.TextField('Detalles', blank=True)
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('Creada', auto_now_add=True)

    class Meta:
        verbose_name = 'Peticion de derechos'
        verbose_name_plural = 'Peticiones de derechos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_right_display()} ({self.get_status_display()})"


class DataExportRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('ready', 'Listo'),
        ('failed', 'Fallido'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='data_export_requests',
    )
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField('Solicitada', auto_now_add=True)
    file = models.FileField('Archivo', upload_to='exports/', blank=True, null=True)

    class Meta:
        verbose_name = 'Solicitud de exportacion'
        verbose_name_plural = 'Solicitudes de exportacion'
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.user.username} ({self.get_status_display()})"


class AccountDeletionRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('scheduled', 'Programada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='account_deletion_requests',
    )
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField('Solicitada', auto_now_add=True)
    scheduled_date = models.DateTimeField('Fecha programada', null=True, blank=True)

    class Meta:
        verbose_name = 'Solicitud de eliminacion de cuenta'
        verbose_name_plural = 'Solicitudes de eliminacion de cuenta'
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.user.username} ({self.get_status_display()})"