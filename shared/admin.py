from django.contrib import admin
from shared.tenant import resolve_tenant_for_user


class TenantAdminMixin:
    """Filtra las consultas del panel admin al municipio del usuario actual.

    - `global_admin` ve todo.
    - `municipal_admin`/`moderator`/`merchant` ven solo su municipio.
    - Modelos sin campo `municipality` (p. ej. BusinessMedia/BusinessHours)
      se filtran a traves del modelo padre (business/category) usando
      `tenant_filter_path` si el admin lo define.
    """

    tenant_filter_path = 'municipality'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user is None or not user.is_authenticated:
            return qs.none()
        if user.role == 'global_admin':
            return qs
        tenant = resolve_tenant_for_user(user)
        if tenant is None:
            return qs.none()
        if self.tenant_filter_path == 'id':
            # El modelo ES el tenant (p. ej. Municipality)
            return qs.filter(id=tenant.id)
        if self.tenant_filter_path == 'municipality':
            if hasattr(qs.model, 'municipality_id'):
                return qs.filter(municipality=tenant)
        else:
            return qs.filter(**{self.tenant_filter_path: tenant})
        return qs

    def has_module_permission(self, request):
        user = request.user
        return user is not None and user.is_authenticated and user.role in ('global_admin', 'municipal_admin', 'moderator', 'merchant')

    def has_view_permission(self, request, obj=None):
        user = request.user
        if user is None or not user.is_authenticated:
            return False
        if user.role == 'global_admin':
            return True
        if obj is None:
            return user.role in ('municipal_admin', 'moderator', 'merchant')
        tenant = resolve_tenant_for_user(user)
        if obj.__class__.__name__ == 'Municipality':
            return obj.id == tenant.id if tenant else False
        if hasattr(obj, 'municipality_id'):
            return obj.municipality_id == tenant.id if tenant else False
        return True

    def save_model(self, request, obj, form, change):
        user = request.user
        if user is not None and user.role != 'global_admin':
            tenant = resolve_tenant_for_user(user)
            if tenant is not None and hasattr(obj, 'municipality_id') and not obj.municipality_id:
                obj.municipality = tenant
        super().save_model(request, obj, form, change)