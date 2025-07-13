from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.response import Response
from users.models import File, TextChunk
from .serializers import FileSerializer, TextChunkSerializer
from rest_framework import status
from django.conf import settings
import boto3
from urllib.parse import urlparse

s3_client = boto3.client(
    's3',
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

class DataRootView(APIView):
    def get(self, request):
        return Response({"message": "Welcome to the Data service root!"})
    
class FileListView(APIView):
    #permission_classes = [IsAuthenticated]
    def get(self, request):
        files = File.objects.all().order_by('-created_at')
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  

class DeleteFileView(APIView):
    # permission_classes = [IsAuthenticated]

    def delete(self, request, file_id):
        try:
            print("Deleting file by hash:", file_id)
            file = File.objects.get(file_id=file_id)

            # Parse full S3 URI: s3://bucket-name/key/path/file.pdf
            parsed = urlparse(file.s3_uri)
            bucket_name = parsed.netloc
            # s3_key = parsed.path.lstrip("/")  # remove leading slash
            s3_key = urlparse(file.s3_uri.decode('utf-8') if isinstance(file.s3_uri, bytes) else file.s3_uri).path.lstrip("/")


            # Delete from S3
            s3_client = boto3.client("s3")
            s3_client.delete_object(Bucket=bucket_name, Key=s3_key)

            # Delete related TextChunk entries
            deleted_chunks, _ = TextChunk.objects.filter(file_hash=file.file_hash).delete()
            
            # Delete File from DB
            file.delete()

            return Response({
                'message': f'File and {deleted_chunks} associated chunks deleted from DB and S3.'
            }, status=status.HTTP_204_NO_CONTENT)

        except File.DoesNotExist:
            serializer = FileSerializer()
            return Response(serializer.data, status=status.HTTP_200_OK)    

class TextChunkCreateView(APIView):
    def post(self, request):
        serializer = TextChunkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)