from django.db import models
from apps.businesses.models import Business
from apps.tenants.models import Municipality
from shared.tenant import TenantManager


class Job(models.Model):
    TYPE_CHOICES = (
        ('full_time', 'Tiempo completo'),
        ('part_time', 'Medio tiempo'),
        ('contract', 'Contrato'),
        ('internship', 'Pasantia'),
        ('freelance', 'Freelance'),
        ('temporary', 'Temporal'),
    )
    MODE_CHOICES = (
        ('onsite', 'Presencial'),
        ('remote', 'Remoto'),
        ('hybrid', 'Hibrido'),
    )
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('closed', 'Cerrado'),
    )

    objects = TenantManager()
    all_objects = models.Manager()

    title = models.CharField('Puesto', max_length=200)
    description = models.TextField('Descripcion')
    requirements = models.TextField('Requisitos', blank=True)
    salary_min = models.DecimalField('Sueldo Min', max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField('Sueldo Max', max_digits=10, decimal_places=2, null=True, blank=True)
    job_type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES, default='full_time')
    work_mode = models.CharField('Modalidad', max_length=20, choices=MODE_CHOICES, default='onsite')

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='jobs',
        null=True,
        blank=True,
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name='jobs',
        null=True,
        blank=True,
    )

    application_email = models.EmailField('Correo de postulacion', blank=True)
    application_url = models.URLField('URL de postulacion', blank=True)
    location = models.CharField('Ubicacion', max_length=255, blank=True)

    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='draft')
    views_count = models.PositiveIntegerField('Vistas', default=0)
    applications_count = models.PositiveIntegerField('Postulaciones', default=0)
    is_featured = models.BooleanField('Destacado', default=False)

    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    expires_at = models.DateTimeField('Expira', null=True, blank=True)

    class Meta:
        verbose_name = 'Empleo'
        verbose_name_plural = 'Empleos'
        ordering = ['-created_at']

    def __str__(self):
        return self.title