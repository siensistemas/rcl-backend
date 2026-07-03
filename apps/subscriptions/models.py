from django.db import models
from apps.tenants.models import Municipality

class Plan(models.Model):
    PLAN_TYPES = (
        ('free', 'Gratuito'),
        ('basic', 'Basico'),
        ('entrepreneur', 'Emprendedor'),
        ('premium', 'Premium'),
        ('enterprise', 'Empresarial'),
    )
    
    name = models.CharField('Nombre', max_length=100)
    plan_type = models.CharField('Tipo', max_length=20, choices=PLAN_TYPES, unique=True)
    description = models.TextField('Descripcion')
    
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='plans',
        null=True,
        blank=True
    )
    
    # Pricing
    price = models.DecimalField('Precio', max_digits=10, decimal_places=2, default=0)
    currency = models.CharField('Moneda', max_length=3, default='COP')
    price_period = models.CharField('Periodo', max_length=10, 
                                   choices=(('monthly', 'Mensual'), ('yearly', 'Anual'), ('lifetime', 'Vitalicio')),
                                   default='monthly')
    
    # Features
    max_images = models.PositiveIntegerField('Max. Imagenes', default=5)
    max_videos = models.PositiveIntegerField('Max. Videos', default=0)
    max_reels = models.PositiveIntegerField('Max. Reels', default=0)
    max_promotions = models.PositiveIntegerField('Max. Promociones', default=0)
    max_products = models.PositiveIntegerField('Max. Productos', default=0)
    max_employees = models.PositiveIntegerField('Max. Empleados', default=0)
    
    # Features flags
    has_analytics = models.BooleanField('Analitica', default=False)
    has_promotions = models.BooleanField('Promociones', default=False)
    has_reels = models.BooleanField('Reels', default=False)
    has_videos = models.BooleanField('Videos', default=False)
    has_geolocation = models.BooleanField('Geolocalizacion', default=False)
    has_notifications = models.BooleanField('Notificaciones', default=False)
    has_api_access = models.BooleanField('API Access', default=False)
    has_advanced_analytics = models.BooleanField('Analitica Avanzada', default=False)
    has_priority_support = models.BooleanField('Soporte Prioritario', default=False)
    
    # Features as JSON for flexibility
    features = models.JSONField('Caracteristicas', default=dict)
    
    # SEO
    is_featured = models.BooleanField('Destacado', default=False)
    is_active = models.BooleanField('Activo', default=True)
    order = models.PositiveIntegerField('Orden', default=0)
    
    created_at = models.DateTimeField('Fecha de Creacion', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de Actualizacion', auto_now=True)

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Planes'
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.name} ({self.get_plan_type_display()})"

    @property
    def is_free(self):
        return self.plan_type == 'free'
    
    @property
    def price_display(self):
        if self.price == 0:
            return 'Gratuito'
        return f" {self.currency}"

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Activa'),
        ('inactive', 'Inactiva'),
        ('expired', 'Expirada'),
        ('cancelled', 'Cancelada'),
        ('pending', 'Pendiente'),
    )
    
    business = models.ForeignKey(
        'businesses.Business',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    
    # Dates
    start_date = models.DateTimeField('Fecha de Inicio')
    end_date = models.DateTimeField('Fecha de Fin')
    renewal_date = models.DateTimeField('Fecha de Renovacion', null=True, blank=True)
    
    # Payment
    payment_method = models.CharField('Metodo de Pago', max_length=50, blank=True)
    payment_reference = models.CharField('Referencia de Pago', max_length=100, blank=True)
    amount_paid = models.DecimalField('Monto Pagado', max_digits=10, decimal_places=2, default=0)
    
    # Status
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='pending')
    auto_renew = models.BooleanField('Renovacion Automatica', default=False)
    
    created_at = models.DateTimeField('Fecha de Creacion', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de Actualizacion', auto_now=True)

    class Meta:
        verbose_name = 'Suscripcion'
        verbose_name_plural = 'Suscripciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.business.name} - {self.plan.name} ({self.status})"

    @property
    def is_active(self):
        from django.utils import timezone
        return self.status == 'active' and self.end_date >= timezone.now()
    
    @property
    def days_remaining(self):
        from django.utils import timezone
        delta = self.end_date - timezone.now()
        return max(0, delta.days)
