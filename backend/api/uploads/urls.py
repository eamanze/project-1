# api/upload/urls.py
from django.urls import path
from .views import UploadAPIRootView, UploadRequestView, UploadCallbackView


urlpatterns = [
    path('', UploadAPIRootView.as_view(), name='upload-root'), 
    path('upload-request/', UploadRequestView.as_view(), name='upload-request'),
    path('upload-callback/', UploadCallbackView.as_view(), name='upload-callback'), 
]