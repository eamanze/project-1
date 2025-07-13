from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
import jwt
        
class CognitoLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Incoming login request data:", request.data)

        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token missing'}, status=400)

        #print("ID Token:", token[:30] + "...")

        # Optional: decode the token and print claims
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            #print("Decoded JWT payload:", decoded)
        except Exception as e:
            return Response({'error': f'JWT decode error: {str(e)}'}, status=400)

        response = Response({'message': 'Logged in'}, status=200)
        response.set_cookie(
            key='id_token',
            value=token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=3600
        )
        return response


# Session check endpoint
class SessionCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.COOKIES.get('id_token')
        if not token:
            return Response({'authenticated': False}, status=401)

        return Response({'authenticated': True}, status=200)

# Logout endpoint
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({'message': 'Logged out'}, status=200)
        response.delete_cookie('id_token')
        return response