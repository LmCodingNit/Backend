from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # authentification endpoints
    path('api/auth/', include('dj_rest_auth.urls')),
    # Registration endpoint 
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # Our app's API endpoints
    path('api/', include('startups.urls')),
    path('api/', include('investors.urls')),
    path('api/chat/', include('chat.urls')), 

]