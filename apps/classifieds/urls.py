from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassifiedViewSet

router = DefaultRouter()
router.register(r'', ClassifiedViewSet, basename='classified')

urlpatterns = [
    path('', include(router.urls)),
]