# backend/api/urls.py
from django.urls import path, include
from .views import APIInfoView, RootAPIView

urlpatterns = [
    path('', RootAPIView.as_view(), name='api-root'),  # Route for /api/
    path('info/', APIInfoView.as_view(), name='api-info'),  # Route for /api/info/

    # Include the URLs from the upload subfolder
    path('uploads/', include('api.uploads.urls')),
    
    # Include the URLs from the search subfolder
    path('search/', include('api.search.urls')),

    # Include the URLs from the data subfolder
    path('data/', include('api.data.urls')),

        
]

'''
# backend/api/urls.py
from django.urls import path
from . import views  

urlpatterns = [
    #path('', views.test_endpoint, name='api_home'),  # Test endpoint
    
]

'''

