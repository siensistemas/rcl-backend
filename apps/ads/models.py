from django.db import models
from apps.businesses.models import Business
from apps.tenants.models import Municipality
from shared.tenant import TenantManager, get_tenant_upload_to


class Ad(models.Model):
    TYPE_CHOICES = (
        ('banner', 'Banner'),
        ('inline', 'Inline'),
        ('video', 'Video'),
    )
    PLACEMENT_CHOICES = (
        ('home', 'Inicio'),
        ('business', 'Comercios'),
        ('detail', 'Detalle de comercio'),
        ('promo_detail', 'Detalle de promocion'),
    )
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('paused', 'Pausado'),
        ('ended', 'Finalizado'),
    )

    objects = TenantManager()
    all_objects = models.Manager()

    title = models.CharField('Titulo', max_length=200)
    description = models.TextField('Descripcion', blank=True)
    ad_type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES, default='banner')
    placement = models.CharField('Ubicacion', max_length=30, choices=PLACEMENT_CHOICES, default='home')
    image = models.ImageField('Imagen', upload_to=get_tenant_upload_to('ads'), blank=True, null=True)
    video = models.FileField('Video', upload_to=get_tenant_upload_to('ads/videos'), blank=True, null=True)
    target_url = models.URLField('URL de destino', blank=True)

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='ads',
        null=True,
        blank=True,
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='ads',
        null=True,
        blank=True,
    )

    start_date = models.DateTimeField('Inicio')
    end_date = models.DateTimeField('Fin')
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='draft')
    views_count = models.PositiveIntegerField('Vistas', default=0)
    clicks_count = models.PositiveIntegerField('Clicks', default=0)

    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Anuncio'
        verbose_name_plural = 'Anuncios'
        ordering = ['-created_at']

    def __str__(self):
        return self.title