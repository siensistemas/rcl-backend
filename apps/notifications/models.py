from django.db import models
from apps.users.models import User
from apps.businesses.models import Business
from shared.tenant import TenantManager


class Notification(models.Model):
    TYPE_CHOICES = (
        ('info', 'Informacion'),
        ('promotion', 'Promocion'),
        ('order', 'Pedido'),
        ('message', 'Mensaje'),
        ('system', 'Sistema'),
    )

    objects = TenantManager()
    all_objects = models.Manager()

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField('Titulo', max_length=200)
    body = models.TextField('Mensaje')
    notification_type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES, default='info')
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
    )
    related_id = models.PositiveIntegerField('ID relacionado', null=True, blank=True)
    is_read = models.BooleanField('Leida', default=False)
    data = models.JSONField('Datos', default=dict, blank=True)

    created_at = models.DateTimeField('Creada', auto_now_add=True)

    class Meta:
        verbose_name = 'Notificacion'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return self.title