import random
import string
import uuid
from django.utils import timezone

def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def generate_uuid():
    return str(uuid.uuid4())

def generate_slug(text, max_length=50):
    from django.utils.text import slugify
    slug = slugify(text)
    if len(slug) > max_length:
        slug = slug[:max_length]
    return slug

def now():
    return timezone.now()

def format_price(amount, currency='COP'):
    return f" {currency}"

def calculate_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371  # Earth radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c
