from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from apps.tenants.models import Municipality
from shared.tenant import get_tenant_upload_to

class User(AbstractUser):
    ROLE_CHOICES = (
        ('global_admin', 'Administrador Global'),
        ('municipal_admin', 'Administrador Municipal'),
        ('merchant', 'Comerciante'),
        ('employee', 'Empleado'),
        ('moderator', 'Moderador'),
        ('user', 'Usuario'),
        ('tourist', 'Turista'),
    )
    
    # Personal Info
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='El telefono debe tener entre 9 y 15 digitos'
    )
    
    role = models.CharField('Rol', max_length=20, choices=ROLE_CHOICES, default='user')
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
)
    phone = models.CharField('Telefono', max_length=20, validators=[phone_regex], blank=True)
    avatar = models.ImageField('Avatar', upload_to=get_tenant_upload_to('users/avatars'), blank=True, null=True)
    cover = models.ImageField('Portada', upload_to=get_tenant_upload_to('users/covers'), blank=True, null=True)
    
    # Verification
    is_verified = models.BooleanField('Verificado', default=False)
    verification_code = models.CharField('Codigo de Verificacion', max_length=6, blank=True, null=True)
    email_verified = models.BooleanField('Email Verificado', default=False)
    phone_verified = models.BooleanField('Telefono Verificado', default=False)
    
    # Profile
    bio = models.TextField('Biografia', max_length=500, blank=True)
    location = models.CharField('Ubicacion', max_length=100, blank=True)
    birth_date = models.DateField('Fecha de Nacimiento', null=True, blank=True)
    gender = models.CharField('Genero', max_length=10, choices=(
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('P', 'Prefiero no decir'),
    ), blank=True)
    
    # Social
    facebook = models.URLField('Facebook', blank=True)
    instagram = models.URLField('Instagram', blank=True)
    twitter = models.URLField('Twitter/X', blank=True)
    linkedin = models.URLField('LinkedIn', blank=True)
    
    # Preferences
    notification_preferences = models.JSONField('Preferencias de Notificacion', default=dict)
    language = models.CharField('Idioma', max_length=10, default='es')
    theme = models.CharField('Tema', max_length=10, choices=(
        ('light', 'Claro'),
        ('dark', 'Oscuro'),
        ('system', 'Sistema'),
    ), default='system')
    
    # Security
    last_login_ip = models.GenericIPAddressField('IP Ultimo Login', null=True, blank=True)
    last_login_device = models.CharField('Dispositivo', max_length=200, blank=True)
    two_factor_enabled = models.BooleanField('2FA Activado', default=False)
    two_factor_secret = models.CharField('Secreto 2FA', max_length=50, blank=True)
    
    # Stats
    login_count = models.PositiveIntegerField('Conteo de Login', default=0)
    
    created_at = models.DateTimeField('Fecha de Registro', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de Actualizacion', auto_now=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} (@{self.username})"

    @property
    def is_merchant(self):
        return self.role in ['merchant', 'employee']

    @property
    def is_admin(self):
        return self.role in ['global_admin', 'municipal_admin']

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def businesses(self):
        if self.role == 'merchant':
            return self.businesses_set.filter(is_active=True)
        return []
