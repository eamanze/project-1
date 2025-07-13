# backend/api/search/urls.py
from django.urls import path
from .views import SearchView

urlpatterns = [
    # Route for search
    path('', SearchView.as_view(), name='file-search'),
    
]
