from django.db import models
from apps.businesses.models import Business
from apps.tenants.models import Municipality
from shared.tenant import TenantManager, get_tenant_upload_to


class Reel(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('inactive', 'Inactivo'),
    )

    objects = TenantManager()
    all_objects = models.Manager()

    title = models.CharField('Titulo', max_length=200)
    description = models.TextField('Descripcion', blank=True)
    video = models.FileField('Video', upload_to=get_tenant_upload_to('reels'))
    thumbnail = models.ImageField('Miniatura', upload_to=get_tenant_upload_to('reels/thumbnails'), blank=True, null=True)

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='reels'
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='reels',
        null=True,
        blank=True,
    )

    duration = models.PositiveIntegerField('Duracion (seg)', default=0)
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='draft')
    views_count = models.PositiveIntegerField('Vistas', default=0)
    likes_count = models.PositiveIntegerField('Me gusta', default=0)
    is_featured = models.BooleanField('Destacado', default=False)

    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Reel'
        verbose_name_plural = 'Reels'
        ordering = ['-created_at']

    def __str__(self):
        return self.title