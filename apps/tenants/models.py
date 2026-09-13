from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from shared.tenant import get_tenant_upload_to

class Municipality(models.Model):
    # Basic Info
    name = models.CharField('Nombre', max_length=100, unique=True)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    description = models.TextField('Descripcion', blank=True)
    slogan = models.CharField('Eslogan', max_length=200, blank=True)
    
    # Branding (cada municipio tiene su propia carpeta de media)
    logo = models.ImageField('Logo', upload_to=get_tenant_upload_to('logos'), blank=True, null=True)
    favicon = models.ImageField('Favicon', upload_to=get_tenant_upload_to('favicons'), blank=True, null=True)
    banner = models.ImageField('Banner', upload_to=get_tenant_upload_to('banners'), blank=True, null=True)
    primary_color = models.CharField('Color Primario', max_length=7, default='#2563eb')
    secondary_color = models.CharField('Color Secundario', max_length=7, default='#7c3aed')
    accent_color = models.CharField('Color de Acento', max_length=7, default='#f59e0b')
    background_color = models.CharField('Color de Fondo', max_length=7, default='#f3f4f6')
    
    # Fonts
    primary_font = models.CharField('Fuente Primaria', max_length=100, default='Inter')
    secondary_font = models.CharField('Fuente Secundaria', max_length=100, default='Roboto')
    
    # Contact
    phone = models.CharField('Telefono', max_length=20, blank=True)
    email = models.EmailField('Correo', blank=True)
    address = models.TextField('Direccion', blank=True)
    website = models.URLField('Sitio Web', blank=True)
    
    # Social Media
    facebook = models.URLField('Facebook', blank=True)
    instagram = models.URLField('Instagram', blank=True)
    twitter = models.URLField('Twitter/X', blank=True)
    youtube = models.URLField('YouTube', blank=True)
    tiktok = models.URLField('TikTok', blank=True)
    
    # Location
    latitude = models.DecimalField('Latitud', max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField('Longitud', max_digits=9, decimal_places=6, null=True, blank=True)
    timezone = models.CharField('Zona Horaria', max_length=50, default='America/Bogota')
    
    # Configuration
    config = models.JSONField('Configuracion', default=dict)
    is_active = models.BooleanField('Activo', default=True)
    is_public = models.BooleanField('Publico', default=True)
    
    # Subscription
    subscription_plan = models.ForeignKey(
        'subscriptions.Plan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='municipalities'
    )
    subscription_expires_at = models.DateTimeField('Expira Suscripcion', null=True, blank=True)
    
    # Stats
    views_count = models.PositiveIntegerField('Visitas', default=0)
    
    created_at = models.DateTimeField('Fecha de Creacion', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de Actualizacion', auto_now=True)

    class Meta:
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def total_businesses(self):
        return self.businesses.filter(is_active=True).count()

    @property
    def total_users(self):
        return self.users.filter(is_active=True).count()

    @property
    def total_events(self):
        return self.events.exclude(status='cancelled').count()

    @property
    def total_promotions(self):
        return self.promotions.filter(status='active').count()

