from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MerchantViewSet

router = DefaultRouter()
router.register(r'', MerchantViewSet, basename='merchant')

urlpatterns = [
    path('', include(router.urls)),
]