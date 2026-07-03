from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

def validate_phone(value):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='El telefono debe tener entre 9 y 15 digitos'
    )
    phone_regex(value)

def validate_colombian_phone(value):
    phone_regex = RegexValidator(
        regex=r'^(\+57)?[3]\d{9}$',
        message='El telefono debe ser un numero valido en Colombia'
    )
    phone_regex(value)

def validate_positive_decimal(value):
    if value < 0:
        raise ValidationError('El valor debe ser positivo')
