from rest_framework import permissions

class IsGlobalAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'global_admin'

class IsMunicipalAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'municipal_admin'

class IsMerchant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'merchant'

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('global_admin', 'municipal_admin')
        )

class IsAdminOrMerchant(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('global_admin', 'municipal_admin', 'merchant')
        )

class IsOwnerOrAdmin(permissions.BasePermission):
    """Solo el dueño del `business` asociado (merchant) o un admin."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role in ('global_admin', 'municipal_admin'):
            return True
        if user.role == 'merchant':
            business = getattr(obj, 'business', None)
            if business is not None and getattr(business, 'owner_id', None) == user.id:
                return True
        return False

class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employee'

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False

class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'moderator'

class IsVerified(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified

class IsActive(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active
