from django.db import models
from apps.tenants.models import Municipality
from shared.tenant import TenantManager, get_tenant_upload_to


class Attraction(models.Model):
    TYPE_CHOICES = (
        ('natural', 'Natural'),
        ('historical', 'Historico'),
        ('cultural', 'Cultural'),
        ('adventure', 'Aventura'),
        ('recreational', 'Recreativo'),
        ('gastronomic', 'Gastronomico'),
        ('other', 'Otro'),
    )
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('inactive', 'Inactivo'),
    )

    objects = TenantManager()
    all_objects = models.Manager()

    name = models.CharField('Nombre', max_length=200)
    description = models.TextField('Descripcion')
    attraction_type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES, default='natural')
    image = models.ImageField('Imagen', upload_to=get_tenant_upload_to('tourism'), blank=True, null=True)
    gallery = models.JSONField('Galeria', default=list, blank=True)

    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='attractions',
        null=True,
        blank=True,
    )

    address = models.CharField('Direccion', max_length=255, blank=True)
    latitude = models.DecimalField('Latitud', max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField('Longitud', max_digits=9, decimal_places=6, null=True, blank=True)

    entry_fee = models.DecimalField('Entrada', max_digits=10, decimal_places=2, default=0)
    is_free = models.BooleanField('Gratuito', default=False)
    opening_hours = models.CharField('Horario', max_length=200, blank=True)

    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='draft')
    views_count = models.PositiveIntegerField('Vistas', default=0)
    is_featured = models.BooleanField('Destacado', default=False)
    is_top_rated = models.BooleanField('Mejor calificado', default=False)

    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Atraccion'
        verbose_name_plural = 'Atracciones'
        ordering = ['name']

    def __str__(self):
        return self.name


class TouristRoute(models.Model):
    objects = TenantManager()
    all_objects = models.Manager()

    name = models.CharField('Nombre', max_length=200)
    description = models.TextField('Descripcion', blank=True)
    image = models.ImageField('Imagen', upload_to=get_tenant_upload_to('tourism/routes'), blank=True, null=True)

    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='tourist_routes',
        null=True,
        blank=True,
    )

    attractions = models.ManyToManyField(Attraction, related_name='routes', blank=True)
    duration_text = models.CharField('Duracion', max_length=100, blank=True)
    is_featured = models.BooleanField('Destacada', default=False)
    views_count = models.PositiveIntegerField('Vistas', default=0)

    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Ruta Turistica'
        verbose_name_plural = 'Rutas Turisticas'

    def __str__(self):
        return self.name