from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalysisReportViewSet, StartupViewSet, TagViewSet

router = DefaultRouter()
router.register(r'startups', StartupViewSet)
router.register(r'tags', TagViewSet)
router.register(r'reports', AnalysisReportViewSet, basename='analysisreport')

urlpatterns = [
    path('', include(router.urls)),
]