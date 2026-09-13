from django.db import models
from apps.businesses.models import Business
from apps.users.models import User
from shared.tenant import TenantManager


class Rating(models.Model):
    objects = TenantManager()
    all_objects = models.Manager()

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rating = models.PositiveSmallIntegerField('Calificacion', default=5)
    comment = models.TextField('Comentario', blank=True)

    created_at = models.DateTimeField('Creada', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizada', auto_now=True)

    class Meta:
        verbose_name = 'Calificacion'
        verbose_name_plural = 'Calificaciones'
        ordering = ['-created_at']
        unique_together = ['business', 'user']

    def __str__(self):
        return f"{self.business.name} - {self.rating}"