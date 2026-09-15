from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConsentViewSet,
    SubmitRightsRequestView,
    RequestDataExportView,
    RequestAccountDeletionView,
)

router = DefaultRouter()
router.register(r'consent', ConsentViewSet, basename='consent')

urlpatterns = [
    path('', include(router.urls)),
    path('rights-request/', SubmitRightsRequestView.as_view()),
    path('data-export/', RequestDataExportView.as_view()),
    path('account-deletion/', RequestAccountDeletionView.as_view()),
]