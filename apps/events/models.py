from django.db import models
from apps.businesses.models import Business
from apps.tenants.models import Municipality
from shared.tenant import TenantManager, get_tenant_upload_to


class Event(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('cancelled', 'Cancelado'),
        ('ended', 'Finalizado'),
    )
    TYPE_CHOICES = (
        ('gastronomy', 'Gastronomia'),
        ('music', 'Musica'),
        ('cultural', 'Cultural'),
        ('sports', 'Deportes'),
        ('commercial', 'Comercial'),
        ('social', 'Social'),
        ('other', 'Otro'),
    )

    objects = TenantManager()
    all_objects = models.Manager()

    title = models.CharField('Titulo', max_length=200)
    description = models.TextField('Descripcion')
    event_type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES, default='other')
    image = models.ImageField('Imagen', upload_to=get_tenant_upload_to('events'), blank=True, null=True)

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True,
        help_text='Negocio que organiza el evento (opcional)',
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True,
    )

    location = models.CharField('Ubicacion', max_length=255, blank=True)
    start_date = models.DateTimeField('Inicio')
    end_date = models.DateTimeField('Fin')

    capacity = models.PositiveIntegerField('Capacidad', null=True, blank=True)
    is_free = models.BooleanField('Gratuito', default=True)
    price = models.DecimalField('Precio', max_digits=10, decimal_places=2, default=0)
    ticket_url = models.URLField('URL de Entradas', blank=True)

    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='draft')
    views_count = models.PositiveIntegerField('Vistas', default=0)
    is_featured = models.BooleanField('Destacado', default=False)

    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-start_date']

    def __str__(self):
        return self.title