# users/views.py

from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_cognito_user(request):
    data = request.data
    email = data.get('email')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    cognito_sub = data.get('sub')  # Optional: Only if your CustomUser has a sub field

    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user already exists
    existing_user = User.objects.filter(username=email).first()
    if existing_user:
        return Response({
            'message': 'User already exists',
            'user_id': existing_user.id,
            'email': existing_user.email
        }, status=status.HTTP_200_OK)

    # Create the new user
    user = User.objects.create_user(
        username=email,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    user.is_staff = True
    user.set_unusable_password()

    # Optional: Save Cognito sub if your model has it
    if hasattr(user, 'sub') and cognito_sub:
        user.sub = cognito_sub

    user.save()

    return Response({
        'message': 'User registered as staff in Django',
        'user_id': user.id,
        'email': user.email
    }, status=status.HTTP_201_CREATED)
