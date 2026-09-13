from django.db import models
from apps.businesses.models import Business
from apps.tenants.models import Municipality
from shared.tenant import TenantManager, get_tenant_upload_to


class Classified(models.Model):
    CATEGORY_CHOICES = (
        ('vehicles', 'Vehiculos'),
        ('real_estate', 'Inmuebles'),
        ('electronics', 'Electronica'),
        ('furniture', 'Muebles'),
        ('fashion', 'Moda'),
        ('services', 'Servicios'),
        ('animals', 'Mascotas'),
        ('jobs', 'Empleo'),
        ('other', 'Otro'),
    )
    CONDITION_CHOICES = (
        ('new', 'Nuevo'),
        ('used', 'Usado'),
        ('refurbished', 'Reacondicionado'),
    )
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('sold', 'Vendido'),
        ('inactive', 'Inactivo'),
    )

    objects = TenantManager()
    all_objects = models.Manager()

    title = models.CharField('Titulo', max_length=200)
    description = models.TextField('Descripcion')
    price = models.DecimalField('Precio', max_digits=12, decimal_places=2, default=0)
    category = models.CharField('Categoria', max_length=30, choices=CATEGORY_CHOICES, default='other')
    condition = models.CharField('Condicion', max_length=20, choices=CONDITION_CHOICES, default='new')
    image = models.ImageField('Imagen', upload_to=get_tenant_upload_to('classifieds'), blank=True, null=True)
    gallery = models.JSONField('Galeria', default=list, blank=True)

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='classifieds',
        null=True,
        blank=True,
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='classifieds',
        null=True,
        blank=True,
    )

    contact_phone = models.CharField('Telefono', max_length=20, blank=True)
    contact_email = models.EmailField('Correo', blank=True)
    location = models.CharField('Ubicacion', max_length=255, blank=True)

    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='draft')
    views_count = models.PositiveIntegerField('Vistas', default=0)
    is_featured = models.BooleanField('Destacado', default=False)

    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Clasificado'
        verbose_name_plural = 'Clasificados'
        ordering = ['-created_at']

    def __str__(self):
        return self.title