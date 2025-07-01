from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestorProfileViewSet

# We use a custom router setup for the investor profile since it's a singleton 'me'
# but we can add the like action to the startup router if we wanted to
# For clarity, let's keep it separate.

# A simple way to handle the 'me' and 'like' endpoints
from . import views

urlpatterns = [
    path('investor/profile/me/', views.InvestorProfileViewSet.as_view({'get': 'me', 'put': 'me'}), name='investor-profile-me'),
    path('investor/recommendations/', views.InvestorProfileViewSet.as_view({'get': 'get_recommendations'}), name='investor-recommendations'),
    path('startups/<int:pk>/like/', views.InvestorProfileViewSet.as_view({'post': 'like_startup'}), name='startup-like'),
]