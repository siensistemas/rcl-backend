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

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'error': True,
            'status_code': response.status_code,
            'message': response.data.get('detail', str(response.data)),
            'data': None
        }
    
    return response
