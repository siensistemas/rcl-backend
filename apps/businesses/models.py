from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.tenants.models import Municipality
from apps.users.models import User
from apps.categories.models import Category
from shared.tenant import TenantManager, get_tenant_upload_to

class Business(models.Model):
    objects = TenantManager()
    all_objects = models.Manager()

    # Basic Info
    name = models.CharField('Nombre', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    short_name = models.CharField('Nombre Corto', max_length=50, blank=True)
    
    # Media (por tenant)
    logo = models.ImageField('Logo', upload_to=get_tenant_upload_to('businesses/logos'), blank=True, null=True)
    cover = models.ImageField('Portada', upload_to=get_tenant_upload_to('businesses/covers'), blank=True, null=True)
    
    # Description
    description = models.TextField('Descripcion')
    history = models.TextField('Historia', blank=True)
    mission = models.TextField('Mision', blank=True)
    vision = models.TextField('Vision', blank=True)
    values = models.TextField('Valores', blank=True)
    
    # Location
    address = models.TextField('Direccion')
    latitude = models.DecimalField('Latitud', max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField('Longitud', max_digits=9, decimal_places=6, null=True, blank=True)
    neighborhood = models.CharField('Barrio', max_length=100, blank=True)
    city = models.CharField('Ciudad', max_length=100, blank=True)
    state = models.CharField('Departamento', max_length=100, blank=True)
    zip_code = models.CharField('Codigo Postal', max_length=20, blank=True)
    
    # Contact
    phone = models.CharField('Telefono', max_length=20)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    email = models.EmailField('Correo', blank=True)
    website = models.URLField('Sitio Web', blank=True)
    
    # Social Media
    facebook = models.URLField('Facebook', blank=True)
    instagram = models.URLField('Instagram', blank=True)
    tiktok = models.URLField('TikTok', blank=True)
    youtube = models.URLField('YouTube', blank=True)
    twitter = models.URLField('Twitter/X', blank=True)
    linkedin = models.URLField('LinkedIn', blank=True)
    pinterest = models.URLField('Pinterest', blank=True)
    
    # Schedule
    schedule = models.JSONField('Horario', default=dict)
    # Ejemplo:
    # {
    #   "monday": {"open": "09:00", "close": "18:00", "closed": false},
    #   "tuesday": {"open": "09:00", "close": "18:00", "closed": false},
    #   ...
    #   "special_days": [
    #       {"date": "2024-12-25", "open": "00:00", "close": "00:00", "closed": true}
    #   ]
    # }
    
    # Relationships
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='businesses'
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='businesses'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='businesses'
    )
    subcategory = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_businesses'
    )
    
    # Features & Services
    features = models.JSONField('Caracteristicas', default=dict)
    # Ejemplo:
    # {
    #   "delivery": true,
    #   "parking": true,
    #   "wifi": true,
    #   "pet_friendly": true,
    #   "card_payment": true,
    #   "air_conditioning": true,
    #   "handicap_accessible": true,
    #   "restrooms": true,
    #   "takeout": true,
    #   "reservations": true
    # }
    
    services = models.JSONField('Servicios', default=dict)
    # Ejemplo:
    # {
    #   "delivery": {"available": true, "price": 5000, "min_order": 20000},
    #   "parking": {"available": true, "price": 0, "capacity": 20},
    #   "wifi": {"available": true, "password": "freewifi"}
    # }
    
    # Payment Methods
    payment_methods = models.JSONField('Metodos de Pago', default=dict)
    # Ejemplo:
    # {
    #   "cash": true,
    #   "card": true,
    #   "nequi": true,
    #   "daviplata": true,
    #   "bank_transfer": true,
    #   "apple_pay": false,
    #   "google_pay": false
    # }
    
    # Verification & Status
    is_verified = models.BooleanField('Verificado', default=False)
    verification_date = models.DateTimeField('Fecha de Verificacion', null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_businesses'
    )
    
    is_active = models.BooleanField('Activo', default=True)
    is_featured = models.BooleanField('Destacado', default=False)
    is_approved = models.BooleanField('Aprobado', default=True)
    approval_date = models.DateTimeField('Fecha de Aprobacion', null=True, blank=True)
    
    # Plan
    plan = models.ForeignKey(
        'subscriptions.Plan',
        on_delete=models.SET_NULL,
        null=True,
        related_name='businesses'
    )
    plan_expires_at = models.DateTimeField('Fecha de Vencimiento del Plan', null=True, blank=True)
    plan_auto_renew = models.BooleanField('Renovacion Automatica', default=False)
    
    # SEO
    meta_title = models.CharField('Meta Title', max_length=200, blank=True)
    meta_description = models.TextField('Meta Description', max_length=300, blank=True)
    meta_keywords = models.CharField('Meta Keywords', max_length=200, blank=True)
    
    # Stats
    views_count = models.PositiveIntegerField('Visitas', default=0)
    clicks_count = models.PositiveIntegerField('Clicks', default=0)
    whatsapp_clicks = models.PositiveIntegerField('Clicks a WhatsApp', default=0)
    call_clicks = models.PositiveIntegerField('Clicks a Llamada', default=0)
    direction_clicks = models.PositiveIntegerField('Clicks a Direccion', default=0)
    website_clicks = models.PositiveIntegerField('Clicks a Website', default=0)
    social_clicks = models.PositiveIntegerField('Clicks a Redes Sociales', default=0)
    favorite_count = models.PositiveIntegerField('Favoritos', default=0)
    share_count = models.PositiveIntegerField('Compartidos', default=0)
    
    created_at = models.DateTimeField('Fecha de Creacion', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de Actualizacion', auto_now=True)

    class Meta:
        verbose_name = 'Comercio'
        verbose_name_plural = 'Comercios'
        ordering = ['-views_count', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.municipality.slug}")
            self.slug = base_slug
            # Ensure uniqueness
            counter = 1
            while Business.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.municipality.name})"

    @property
    def rating_average(self):
        ratings = self.ratings.all()
        if ratings:
            return round(sum(r.rating for r in ratings) / ratings.count(), 2)
        return 0

    @property
    def total_ratings(self):
        return self.ratings.count()

    @property
    def rating_distribution(self):
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in self.ratings.all():
            distribution[int(rating.rating)] += 1
        return distribution

    @property
    def is_open_now(self):
        from datetime import datetime
        now = datetime.now()
        day = now.strftime('%A').lower()
        current_time = now.strftime('%H:%M')
        
        if day in self.schedule:
            schedule = self.schedule[day]
            if schedule.get('closed', False):
                return False
            if schedule.get('open') and schedule.get('close'):
                return schedule['open'] <= current_time <= schedule['close']
        return False

    @property
    def plan_name(self):
        return self.plan.name if self.plan else 'Sin Plan'

    @property
    def plan_type(self):
        return self.plan.plan_type if self.plan else 'free'

class BusinessMedia(models.Model):
    MEDIA_TYPES = (
        ('image', 'Imagen'),
        ('video', 'Video'),
        ('reel', 'Reel'),
    )
    
    objects = TenantManager()
    all_objects = models.Manager()

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='media'
    )
    media_type = models.CharField('Tipo', max_length=10, choices=MEDIA_TYPES)
    file = models.FileField('Archivo', upload_to=get_tenant_upload_to('businesses/media'))
    thumbnail = models.ImageField('Miniatura', upload_to=get_tenant_upload_to('businesses/thumbnails'), blank=True, null=True)
    title = models.CharField('Titulo', max_length=200, blank=True)
    description = models.TextField('Descripcion', blank=True)
    is_cover = models.BooleanField('Portada', default=False)
    is_featured = models.BooleanField('Destacado', default=False)
    order = models.PositiveIntegerField('Orden', default=0)
    views_count = models.PositiveIntegerField('Visitas', default=0)
    
    created_at = models.DateTimeField('Fecha de Subida', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de Actualizacion', auto_now=True)

    class Meta:
        verbose_name = 'Media del Comercio'
        verbose_name_plural = 'Medias del Comercio'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.business.name} - {self.media_type}"

class BusinessHours(models.Model):
    DAYS = (
        ('monday', 'Lunes'),
        ('tuesday', 'Martes'),
        ('wednesday', 'Miercoles'),
        ('thursday', 'Jueves'),
        ('friday', 'Viernes'),
        ('saturday', 'Sabado'),
        ('sunday', 'Domingo'),
    )
    
    objects = TenantManager()
    all_objects = models.Manager()

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='hours'
    )
    day = models.CharField('Dia', max_length=10, choices=DAYS)
    open_time = models.TimeField('Hora de Apertura', null=True, blank=True)
    close_time = models.TimeField('Hora de Cierre', null=True, blank=True)
    is_closed = models.BooleanField('Cerrado', default=False)
    
    class Meta:
        verbose_name = 'Horario del Comercio'
        verbose_name_plural = 'Horarios del Comercio'
        unique_together = ['business', 'day']
        ordering = ['day']

    def __str__(self):
        if self.is_closed:
            return f"{self.business.name} - {self.get_day_display()}: Cerrado"
        return f"{self.business.name} - {self.get_day_display()}: {self.open_time} - {self.close_time}"
