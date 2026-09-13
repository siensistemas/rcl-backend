from django.db import models
from apps.businesses.models import Business
from shared.tenant import TenantManager


class AnalyticEvent(models.Model):
    EVENT_TYPES = (
        ('view', 'Visita'),
        ('click', 'Click'),
        ('claim', 'Canje'),
        ('share', 'Compartido'),
        ('favorite', 'Favorito'),
    )

    objects = TenantManager()
    all_objects = models.Manager()

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    event_type = models.CharField('Tipo', max_length=20, choices=EVENT_TYPES)
    source = models.CharField('Fuente', max_length=50, blank=True, default='app')
    meta = models.JSONField('Metadatos', default=dict, blank=True)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='analytic_events',
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField('Fecha', auto_now_add=True)

    class Meta:
        verbose_name = 'Evento analitico'
        verbose_name_plural = 'Eventos analiticos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business', 'event_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.business.name} - {self.event_type} - {self.created_at}"