# api/upload/serializers.py
from rest_framework import serializers
from users.models import File, TextChunk
from django.contrib.auth import get_user_model

User = get_user_model()

class FileSerializer(serializers.ModelSerializer):
    uploaded_by_user = serializers.SerializerMethodField()
    class Meta:
        model = File
        fields = ['file_id', 'file_name', 's3_uri', 'cdn_url', 'file_status','processed_flag','uploaded_by_user','created_at']
    
    def get_uploaded_by_user(self, obj):
        user = obj.uploaded_by_user_id  # model field is 'uploaded_by_user_id'
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        return None
    
class TextChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextChunk
        fields = '__all__'