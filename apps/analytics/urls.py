from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticViewSet

router = DefaultRouter()
router.register(r'', AnalyticViewSet, basename='analytic')

urlpatterns = [
    path('', include(router.urls)),
]