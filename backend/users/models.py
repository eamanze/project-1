from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth import get_user_model
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is a required field')
    
        email = self.normalize_email(email)
        user = self.model(email = email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
        

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
        


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=200, unique=True)
    username = models.CharField(max_length=200, null=True, blank=True)

    # Add as many custom fields as needed
    member_code = models.BigIntegerField(null=False, blank=False, default=000000) # Add member_code as a mandatory custom field

    # Tell Django to use the CustomUserManager
    objects = CustomUserManager()

    # Specifying email as the user name
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class File(models.Model):
    file_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255)
    s3_uri = models.URLField(max_length=1024, unique=True, null=True, blank=True)
    cdn_url = models.URLField(unique=True, null=True, blank=True)
    file_hash = models.TextField(unique=True)
    processed_flag = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    uploaded_by_user_id = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, related_name='uploaded_files')
    created_at = models.DateTimeField(auto_now_add=True)

    # New field: file_status
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FILE_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
    ]

    file_status = models.CharField(
        max_length=20,
        choices=FILE_STATUS_CHOICES,
        default=PENDING,  # Default status is 'Pending'
    )

    def __str__(self):
        return self.file_name

class TextChunk(models.Model):
    file_hash = models.CharField(max_length=255, db_index=True)  # Identify which document this chunk belongs to
    chunk_text = models.TextField()                              # The actual chunk content
    chunk_number = models.IntegerField()                         # The order/position of this chunk
    vector_id = models.CharField(max_length=255, null=True, blank=True)  # Pinecone vector ID, initially null
    model_used = models.CharField(max_length=255)                # Which model generated this (e.g., textembedding-gecko)

    created_at = models.DateTimeField(auto_now_add=True)         # When chunk was created
    updated_at = models.DateTimeField(auto_now=True)             # Last update time (e.g., when vector ID is set)

    class Meta:
        unique_together = ('file_hash', 'chunk_number')
        ordering = ['file_hash', 'chunk_number']

    def __str__(self):
        return f"Chunk {self.chunk_number} of {self.file_hash}"
        
'''
class Chunk(models.Model):
    # Chunk ID (UUID as primary key)
    chunk_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Foreign Key to File (a chunk belongs to a specific file)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='chunks')

    # Chunk number (integer to denote the order of the chunk)
    chunk_number = models.IntegerField()

    # Chunk text (the actual text data of the chunk)
    chunk_text = models.TextField()

    # Timestamp for when the chunk was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chunk {self.chunk_number} of {self.file.file_name}"
    

class Embedding(models.Model):
    # Embedding ID (string as primary key)
    embedding_id = models.CharField(max_length=255, primary_key=True)  # Primary Key

    # The vector field (storing the vector data as a list of floats or a JSON structure)
    vector = models.JSONField()  # You can use JSONField to store the vector

    # Foreign Key to the Chunk model (One-to-One relationship with Chunk)
    chunk = models.OneToOneField(Chunk, on_delete=models.CASCADE, related_name='embedding')

    # Timestamp for when the embedding was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Embedding for Chunk {self.chunk.chunk_number}"

'''