from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttractionViewSet, TouristRouteViewSet

router = DefaultRouter()
router.register(r'attractions', AttractionViewSet, basename='attraction')
router.register(r'routes', TouristRouteViewSet, basename='tourist-route')

urlpatterns = [
    path('', include(router.urls)),
]