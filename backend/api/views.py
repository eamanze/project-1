# backend/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response

class RootAPIView(APIView):
    def get(self, request):
        return Response({"message": "Welcome to the API root!"})

class APIInfoView(APIView):
    def get(self, request):
        return Response({"version": "1.0", "status": "active"})
    

'''
# backend/api/views.py
from django.http import JsonResponse

def test_endpoint(request):
    return JsonResponse({"status": "API is working!"})

'''