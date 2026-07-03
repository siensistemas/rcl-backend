from django.db import transaction
from django.db.models import Q
from geopy.distance import geodesic
from .models import Business
from .serializers import BusinessSerializer

class BusinessService:
    @staticmethod
    def get_nearby_businesses(lat, lng, radius_km=5, limit=20):
        businesses = Business.objects.filter(is_active=True, is_approved=True)
        nearby = []
        for business in businesses:
            if business.latitude and business.longitude:
                distance = geodesic(
                    (float(lat), float(lng)),
                    (float(business.latitude), float(business.longitude))
                ).km
                if distance <= radius_km:
                    nearby.append({
                        'business': business,
                        'distance': round(distance, 2)
                    })
        return sorted(nearby, key=lambda x: x['distance'])[:limit]
    
    @staticmethod
    def search_businesses(query, municipality_id=None, category_id=None):
        q = Q(name__icontains=query) | Q(description__icontains=query) | Q(short_name__icontains=query)
        
        if municipality_id:
            q &= Q(municipality_id=municipality_id)
        if category_id:
            q &= Q(category_id=category_id) | Q(subcategory_id=category_id)
        
        return Business.objects.filter(q, is_active=True, is_approved=True)
    
    @staticmethod
    def get_featured_businesses(municipality_id=None, limit=10):
        q = Q(is_featured=True, is_active=True, is_approved=True)
        if municipality_id:
            q &= Q(municipality_id=municipality_id)
        return Business.objects.filter(q).order_by('-views_count')[:limit]
    
    @staticmethod
    def get_business_stats(business_id):
        business = Business.objects.get(id=business_id)
        return {
            'views': business.views_count,
            'clicks': business.clicks_count,
            'whatsapp': business.whatsapp_clicks,
            'calls': business.call_clicks,
            'directions': business.direction_clicks,
            'website': business.website_clicks,
            'social': business.social_clicks,
            'favorites': business.favorite_count,
            'shares': business.share_count,
            'rating': business.rating_average,
            'total_ratings': business.total_ratings,
        }
