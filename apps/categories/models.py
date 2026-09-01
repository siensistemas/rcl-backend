from django.db import models
from django.utils.text import slugify
from apps.tenants.models import Municipality
from shared.tenant import TenantManager, get_tenant_upload_to

class Category(models.Model):
    objects = TenantManager()
    all_objects = models.Manager()

    name = models.CharField('Nombre', max_length=100)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    description = models.TextField('Descripcion', blank=True)
    icon = models.CharField('Icono (FontAwesome)', max_length=50, default='fa-store')
    icon_color = models.CharField('Color del Icono', max_length=7, default='#2563eb')
    image = models.ImageField('Imagen', upload_to=get_tenant_upload_to('categories'), blank=True, null=True)
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank=True
    )
    
    is_active = models.BooleanField('Activa', default=True)
    is_featured = models.BooleanField('Destacada', default=False)
    order = models.PositiveIntegerField('Orden', default=0)
    
    created_at = models.DateTimeField('Fecha de Creacion', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de Actualizacion', auto_now=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['order', 'name']
        unique_together = ['name', 'municipality']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.municipality.name if self.municipality else 'Global'})"

    @property
    def total_businesses(self):
        return self.businesses.filter(is_active=True).count()
    
    @property
    def depth(self):
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth
