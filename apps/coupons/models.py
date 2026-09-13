from django.db import models
from apps.businesses.models import Business
from apps.promotions.models import Promotion
from apps.users.models import User
from shared.tenant import TenantManager


class Coupon(models.Model):
    STATUS_CHOICES = (
        ('active', 'Activo'),
        ('used', 'Usado'),
        ('expired', 'Expirado'),
    )

    objects = TenantManager()
    all_objects = models.Manager()

    code = models.CharField('Codigo', max_length=50, unique=True)
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name='coupons'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='coupons'
    )
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='active')
    redeemed_at = models.DateTimeField('Canjeado', null=True, blank=True)
    expires_at = models.DateTimeField('Expira', null=True, blank=True)

    created_at = models.DateTimeField('Creado', auto_now_add=True)

    class Meta:
        verbose_name = 'Cupon'
        verbose_name_plural = 'Cupones'
        ordering = ['-created_at']

    def __str__(self):
        return self.code