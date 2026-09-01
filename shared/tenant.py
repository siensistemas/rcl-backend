import os
from contextvars import ContextVar
from django.db import models

# ---------------------------------------------------------------------------
# Tenant context — almacena el Municipality actual para toda la request
# ---------------------------------------------------------------------------
_current_tenant: ContextVar = ContextVar('current_tenant', default=None)


def get_current_tenant():
    return _current_tenant.get()


def set_current_tenant(municipality):
    _current_tenant.set(municipality)


def clear_current_tenant():
    _current_tenant.set(None)


# ---------------------------------------------------------------------------
# Upload-to dinamico por tenant
# Estructura: media/tenants/{municipality_id}/{sub_path}/{filename}
# Si no hay tenant activo, cae a media/general/{sub_path}/{filename}
# ---------------------------------------------------------------------------
class TenantUploadTo:
    """Callable serializable que Django puede guardar en migraciones."""

    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        tenant = get_current_tenant()
        if tenant is not None:
            return os.path.join('tenants', str(tenant.id), self.sub_path, filename)
        # Si el instance tiene municipality FK, usarlo directamente
        if hasattr(instance, 'municipality_id') and instance.municipality_id:
            return os.path.join('tenants', str(instance.municipality_id), self.sub_path, filename)
        # Si el instance se relaciona con una Business, usar su municipality
        if hasattr(instance, 'business_id') and instance.business_id:
            return os.path.join('tenants', str(instance.business.municipality_id), self.sub_path, filename)
        # Si el instance ES un Municipality, usar su propio id
        if instance.__class__.__name__ == 'Municipality' and instance.pk:
            return os.path.join('tenants', str(instance.pk), self.sub_path, filename)
        return os.path.join('general', self.sub_path, filename)

    def deconstruct(self):
        return ('shared.tenant.TenantUploadTo', [self.sub_path], {})


def get_tenant_upload_to(sub_path):
    return TenantUploadTo(sub_path)


# ---------------------------------------------------------------------------
# TenantQuerySet — filtra automáticamente por tenant actual
# ---------------------------------------------------------------------------
class TenantQuerySet(models.QuerySet):
    def filter_by_tenant(self):
        tenant = get_current_tenant()
        if tenant is None:
            return self  # Sin tenant → sin filtro (API publica o sin auth)

        model = self.model
        # Ruta 1: FK municipality directa
        if hasattr(model, 'municipality'):
            return self.filter(municipality=tenant)
        # Ruta 2: FK business (Promotion, BusinessMedia, etc.)
        if hasattr(model, 'business'):
            return self.filter(business__municipality=tenant)
        # Ruta 3: FK owner con municipality (User directo)
        if hasattr(model, 'owner') and hasattr(model.owner.field.remote_field.model, 'municipality'):
            return self.filter(owner__municipality=tenant)
        return self


# ---------------------------------------------------------------------------
# TenantManager — manager que filtra por tenant automáticamente
# ---------------------------------------------------------------------------
class TenantManager(models.Manager):
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db).filter_by_tenant()

    def all_unfiltered(self):
        """Devuelve todas las filas sin filtro de tenant (para global_admin)."""
        return super().get_queryset()


# ---------------------------------------------------------------------------
# Atajo para views: obtener el tenant del request/user
# ---------------------------------------------------------------------------
def resolve_tenant_for_user(user):
    from apps.tenants.models import Municipality

    if user is None or not getattr(user, 'is_authenticated', False):
        return None
    role = getattr(user, 'role', None)
    muni = getattr(user, 'municipality', None)
    if role in ('global_admin',):
        return None  # global_admin no se restringe a un tenant
    if muni is not None and getattr(muni, 'is_active', False):
        return muni
    return None