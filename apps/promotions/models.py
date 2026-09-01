from django.db import models
from apps.businesses.models import Business
from shared.tenant import TenantManager, get_tenant_upload_to

class Promotion(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('active', 'Activa'),
        ('inactive', 'Inactiva'),
        ('expired', 'Expirada'),
        ('cancelled', 'Cancelada'),
    )
    
    DISCOUNT_TYPES = (
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto Fijo'),
        ('bogo', '2x1'),
        ('free_shipping', 'Envio Gratis'),
    )
    
    objects = TenantManager()
    all_objects = models.Manager()

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='promotions'
    )
    
    # Basic Info
    title = models.CharField('Titulo', max_length=200)
    subtitle = models.CharField('Subtitulo', max_length=200, blank=True)
    description = models.TextField('Descripcion')
    
    # Media (por tenant, via business)
    image = models.ImageField('Imagen', upload_to=get_tenant_upload_to('promotions/images'), blank=True, null=True)
    video = models.FileField('Video', upload_to=get_tenant_upload_to('promotions/videos'), blank=True, null=True)
    gallery = models.JSONField('Galeria', default=list)
    
    # Validity
    start_date = models.DateTimeField('Fecha de Inicio')
    end_date = models.DateTimeField('Fecha de Fin')
    
    # Conditions
    conditions = models.TextField('Condiciones', blank=True)
    terms = models.TextField('Terminos y Condiciones', blank=True)
    
    # Quantity
    available_quantity = models.PositiveIntegerField('Cantidad Disponible', default=0)
    used_quantity = models.PositiveIntegerField('Cantidad Usada', default=0)
    max_per_user = models.PositiveIntegerField('Maximo por Usuario', default=1)
    
    # Discount
    discount_type = models.CharField('Tipo de Descuento', max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField('Valor del Descuento', max_digits=10, decimal_places=2, default=0)
    min_purchase = models.DecimalField('Compra Minima', max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField('Descuento Maximo', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField('Destacada', default=False)
    is_unlimited = models.BooleanField('Ilimitada', default=False)
    
    # Stats
    views_count = models.PositiveIntegerField('Vistas', default=0)
    redeemed_count = models.PositiveIntegerField('Canjeadas', default=0)
    clicks_count = models.PositiveIntegerField('Clicks', default=0)
    share_count = models.PositiveIntegerField('Compartidos', default=0)
    
    created_at = models.DateTimeField('Fecha de Creacion', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de Actualizacion', auto_now=True)

    class Meta:
        verbose_name = 'Promocion'
        verbose_name_plural = 'Promociones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.business.name} - {self.title}"

    @property
    def remaining_quantity(self):
        if self.is_unlimited:
            return 999999
        return max(0, self.available_quantity - self.used_quantity)

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return self.status == 'active' and self.start_date <= now <= self.end_date
    
    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return 0
    
    @property
    def usage_percentage(self):
        if self.available_quantity > 0:
            return round((self.used_quantity / self.available_quantity) * 100, 2)
        return 0
