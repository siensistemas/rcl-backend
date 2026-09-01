from .tenant import set_current_tenant, clear_current_tenant


class TenantMiddleware:
    """
    Middleware que setea el tenant (Municipality) actual en cada request.

    Flujo:
      1. Extrae el usuario del JWT (SimpleJWT ya lo puso en request.user)
      2. Si el usuario tiene municipality, lo usa como tenant
      3. Si el usuario es global_admin, intenta leer X-Tenant-ID del header
         (para que un admin pueda operar sobre otro municipio)
      4. Al finalizar la request, limpia el contexto
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = self._resolve_tenant(request)
        set_current_tenant(tenant)

        try:
            response = self.get_response(request)
        finally:
            clear_current_tenant()

        return response

    def _resolve_tenant(self, request):
        user = getattr(request, 'user', None)

        # Si el usuario no está autenticado (API publica), permitir seleccionar
        # el municipio via header X-Tenant-ID o query param ?municipality=X
        if user is None or not getattr(user, 'is_authenticated', False):
            tenant_id = request.headers.get('X-Tenant-ID') or request.GET.get('municipality')
            return self._get_municipality(tenant_id)

        # global_admin puede elegir tenant via header X-Tenant-ID
        if getattr(user, 'role', None) == 'global_admin':
            tenant_id = request.headers.get('X-Tenant-ID')
            if tenant_id:
                return self._get_municipality(tenant_id)

        # Para todos los demás usuarios, usar su municipality asignado
        municipality = getattr(user, 'municipality', None)
        if municipality is not None and getattr(municipality, 'is_active', False):
            return municipality

        return None

    def _get_municipality(self, tenant_id):
        if not tenant_id:
            return None
        from apps.tenants.models import Municipality
        try:
            return Municipality.objects.get(id=tenant_id, is_active=True)
        except (Municipality.DoesNotExist, ValueError, TypeError):
            return None
