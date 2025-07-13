
from django.contrib import admin
from django.urls import path, include
from .views import CognitoLoginView, LogoutView, SessionCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', include('users.urls'))
    # Include the API URLs
    path('api/', include('api.urls')),  
    path('api/users/', include('users.urls')), 

    # Include the auth URLs
    path('api/auth/login/', CognitoLoginView.as_view(), name='cognito-login'),
    path('api/auth/session/', SessionCheckView.as_view(), name='session-check'),    
    path('api/auth/logout/', LogoutView.as_view(), name='cognito-logout'),

]
