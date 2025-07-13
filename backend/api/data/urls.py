# backend/api/data/urls.py
from django.urls import path
from .views import DataRootView, FileListView, DeleteFileView, TextChunkCreateView

urlpatterns = [
    # Route for data service
    path('', DataRootView.as_view(), name='data-service'),
    path('files/', FileListView.as_view(), name='file-list'),
    path('files/<str:file_id>/', DeleteFileView.as_view(), name='delete-file'),
    path('chunks/', TextChunkCreateView.as_view()), 
    
]
