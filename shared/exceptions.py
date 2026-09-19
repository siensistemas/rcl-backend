from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status

class BusinessError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error en el negocio'
    default_code = 'business_error'

class PermissionDeniedError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permiso denegado'
    default_code = 'permission_denied'

class NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Recurso no encontrado'
    default_code = 'not_found'

def _extract_detail_message(data):
    """Extrae un mensaje legible del detalle de error de DRF, que puede ser
    un dict (errores por campo), una lista o un string."""
    if isinstance(data, dict):
        if 'detail' in data:
            return _extract_detail_message(data['detail'])
        parts = []
        for key, value in data.items():
            parts.append(f'{key}: {_extract_detail_message(value)}')
        return '; '.join(parts)
    if isinstance(data, (list, tuple)):
        parts = [_extract_detail_message(item) for item in data]
        return '; '.join(filter(None, parts))
    if hasattr(data, 'title') and hasattr(data, '_data'):
        return str(data)
    return str(data)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'error': True,
            'status_code': response.status_code,
            'message': _extract_detail_message(response.data),
            'data': None
        }

    return response
