from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
import re
import jwt
from rest_framework.authentication import get_authorization_header
import httpx
from users.models import File
from api.serializers import FileSerializer

class SearchView(APIView):
    def get(self, request):
        raw_query = request.GET.get('query', '')
        query = self.clean_search_query(raw_query)

        token = request.COOKIES.get('id_token')
        if not token:
            auth = get_authorization_header(request).split()
            if auth and auth[0].lower() == b'bearer' and len(auth) == 2:
                token = auth[1].decode('utf-8')

        if not token:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)

        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_email = decoded.get("email")
        except jwt.DecodeError:
            return Response({'error': 'Invalid JWT'}, status=401)

        User = get_user_model()
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({'error': 'User not found in Django'}, status=401)

        # 🚀 Call FastAPI's /search endpoint
        try:
            fastapi_url = "http://aifastapi:8010/search"
            try:
                threshold = float(request.GET.get("threshold", "0.75"))
            except ValueError:
                threshold = 0.75

            payload = {
                "query": query,
                "top_k": 5,
                "threshold": threshold
            }

            response = httpx.post(fastapi_url, json=payload, timeout=15.0)

            if response.status_code != 200:
                return Response(
                    {
                        "error": "FastAPI error",
                        "status_code": response.status_code,
                        "detail": response.text or response.reason_phrase or "Unknown error"
                    },
                    status=response.status_code
                )

            fastapi_data = response.json()
            file_id = fastapi_data.get("file_id")
            response_text = fastapi_data.get("response")

            if not file_id or not response_text:
                return Response({"error": "No response generated."}, status=404)

            # ✅ Fetch file object from DB
            try:
                file_obj = File.objects.get(file_hash=file_id)
            except File.DoesNotExist:
                return Response({"error": "File not found in database"}, status=404)

            serialized_file = FileSerializer(file_obj)

            return Response({
                "file": serialized_file.data,
                "response": response_text
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def clean_search_query(self, query: str) -> str:
        # Normalize whitespace
        query = query.strip()

        # Remove any suspicious characters except safe ones like punctuation
        query = re.sub(r"[^a-zA-Z0-9\s\?\!\.\-']", "", query)

        # Collapse multiple spaces to one
        query = re.sub(r"\s+", " ", query)

        return query
