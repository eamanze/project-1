# api/upload/views.py
import boto3
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.authentication import get_authorization_header
from django.conf import settings
import jwt
from django.utils import timezone
from users.models import File
from api.uploads import tasks

from .utils.dynamodb_locks import (
    create_dynamodb_lock,
    delete_dynamodb_lock,
    dynamodb_lock_exists
)


s3_client = boto3.client(
    's3',
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
CLOUDFRONT_DOMAIN = settings.AWS_CDN_BASE_URL

class UploadRequestView(APIView):
    permission_classes = []  # Customize later with token middleware if needed

    def post(self, request, *args, **kwargs):
        # --- Auth Handling ---
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

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({'error': 'User not found in Django'}, status=401)

        # --- Validate Inputs ---
        file_hash = request.data.get('file_hash')
        file_name = request.data.get('file_name')
        file_size = request.data.get('file_size')

        if not (file_hash and file_name and file_size):
            return Response({"error": "Missing required fields."}, status=400)

        # --- Check Postgres First ---
        file_obj = File.objects.filter(file_hash=file_hash).first()
        if file_obj:
            # Already exists in DB, return existing info
            return Response({
                'message': 'File already exists',
                'file_name': file_obj.file_name,
                'file_hash': file_obj.file_hash,
                'file_status': file_obj.file_status,
                's3_uri': file_obj.s3_uri,
                'cdn_url': file_obj.cdn_url
            }, status=200)

        # --- Create Lock in DynamoDB ---
        if dynamodb_lock_exists(file_hash):
            return Response({'detail': 'File is already being uploaded'}, status=409)

        if not create_dynamodb_lock(file_hash):
            return Response({'detail': 'Failed to acquire lock'}, status=423)

        print('bingo 1: file name:', file_name, ', hash:', file_hash)
        # --- Create File Record ---
        file_obj = File.objects.create(
            file_name=file_name,
            file_hash=file_hash,
            uploaded_by_user_id=user,
            file_status=File.PENDING
        )
        print('bingo 2')
        # --- Generate S3 Presigned URL ---
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': S3_BUCKET, 
                'Key': f'uploads/{file_hash}.pdf',
                'ContentType': 'application/pdf'

            },
            ExpiresIn=3600,
            HttpMethod='PUT'
        )
        print('bingo 3')
        return Response({
            'upload_url': presigned_url,
            'file_hash': file_hash,
            'file_name': file_name
        }, status=200)

    
class UploadCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        file_hash = request.data.get('file_hash')
        s3_uri = str(request.data.get('s3_uri'))
        #cdn_url = request.data.get('cdn_url', '')  # Optional
        cdn_url =  self.s3_uri_to_cdn(s3_uri)

        print("🔁 Upload callback received:")
        print("file_hash:", file_hash)
        print("s3_uri:", s3_uri)
        print("cdn_url:", cdn_url)

        if not file_hash or not s3_uri:
            return Response({'error': 'Missing file_hash or s3_uri'}, status=400)

        file = File.objects.filter(file_hash=file_hash).first()
        if not file:
            return Response({'error': 'File not found in database'}, status=404)

        # Optional: check if the object really exists in S3
        try:
            s3_client.head_object(Bucket=S3_BUCKET, Key=f'uploads/{file_hash}.pdf')
        except s3_client.exceptions.ClientError as e:
            return Response({'error': 'File not found in S3'}, status=404)

        # Update file record
        file.s3_uri = s3_uri
        file.cdn_url = cdn_url #or s3_uri
        file.file_status = File.COMPLETED
        file.processed_at = timezone.now()
        file.save()

        # Clean up lock
        delete_dynamodb_lock(file_hash)

        print(f"File {file.file_name} marked as COMPLETED and unlocked.")

        task = tasks.process_text.delay(file.file_hash, file.s3_uri)
        if task:
            return Response({'message': 'Task queued for text processing'}, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': 'File status updated successfully',
            'file_name': file.file_name,
            'file_status': file.file_status,
            'processed_at': file.processed_at.isoformat()
        }, status=200)
    
    def s3_uri_to_cdn(self, s3_uri: str) -> str:
        """
        Converts s3://bucket/key.pdf → https://<cloudfront>/key.pdf
        """
        if not s3_uri.startswith("s3://"):
            raise ValueError("Invalid S3 URI format")

        parts = s3_uri.replace("s3://", "").split("/", 1)
        if len(parts) != 2:
            raise ValueError("Malformed S3 URI")

        key = parts[1]  # just the file path
        return f"{CLOUDFRONT_DOMAIN}/{key}"


class UploadAPIRootView(APIView):
    def get(self, request):
        return Response({
            "description": "Upload API Root",
            "endpoints": 
                [
                    {
                    "upload-request": {
                        "endpoint":"/api/upload/upload-request", # Test via Postman/ curl: - curl -X POST http://127.0.0.1:8000/api/upload/upload-request/  
                        "method": "POST",
                        }
                    },
                    {
                    "upload-callback": {
                        "endpoint":"/api/upload/upload-callback/",  # Test via Postman/ curl: - curl -X POST http://127.0.0.1:8000/api/upload/upload-callback/ 
                        "method": "POST",
                        }
                    }
                ]
        })



'''
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import hashlib
import boto3
from django.conf import settings


s3_client = boto3.client(
    's3',
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME

class UploadAPIRootView(APIView):
    def get(self, request):
        return Response({
            "description": "Upload API Root",
            "endpoints": 
                [
                    {
                    "upload-request": {
                        "endpoint":"/api/upload/upload-request", # Test via Postman/ curl: - curl -X POST http://127.0.0.1:8000/api/upload/upload-request/  
                        "method": "POST",
                        }
                    },
                    {
                    "upload-callback": {
                        "endpoint":"/api/upload/upload-callback/",  # Test via Postman/ curl: - curl -X POST http://127.0.0.1:8000/api/upload/upload-callback/ 
                        "method": "POST",
                        }
                    }
                ]
        })


class UploadRequestView(APIView):
    def post(self, request, *args, **kwargs):
        # Simple demo response explaining what the upload API does
        return Response(
            {"message": "The upload API allows clients to upload files to S3 by generating a signed URL. "
                        "You send a 'file_hash', 'file_name', and 'file_size' to request a signed URL for uploading."},
            status=status.HTTP_200_OK
        )

class UploadCallbackView(APIView): 
    def post(self, request, *args, **kwargs):
        # Simple demo response explaining the callback API
        return Response(
            {"message": "The upload callback API is used to notify the backend after the file is uploaded "
                        "to S3. It receives the 'file_hash', 's3_uri', and 'cdn_url' to update the file status."},
            status=status.HTTP_200_OK
        )

'''