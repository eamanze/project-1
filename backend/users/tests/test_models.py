# tests/test_models.py

import pytest
from users.models import File, Chunk, Embedding
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

@pytest.mark.django_db
def test_file_status_field():
    user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='password')

    # Create a file with 'PENDING' status
    file = File.objects.create(
        file_name="test_file.txt",
        s3_uri="https://s3.amazonaws.com/mybucket/test_file.txt",
        cdn_url="https://cdn.example.com/test_file.txt",
        file_hash="testhashvalue",
        uploaded_by_user_id=user,
    )
    
    # Assert the file's initial status is 'PENDING'
    assert file.file_status == File.PENDING
    
    # Update the file status to 'COMPLETED'
    file.file_status = File.COMPLETED
    file.save()

    # Assert the file's status is now 'COMPLETED'
    assert file.file_status == File.COMPLETED


@pytest.mark.django_db
def test_chunk_creation():
    # Create a user (if necessary)
    user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='password')

    # Create a file instance (this is assuming you already have a file in the system)
    file = File.objects.create(
        file_name="dummy_file.txt",
        s3_uri="https://s3.amazonaws.com/mybucket/dummy_file.txt",
        cdn_url="https://cdn.example.com/dummy_file.txt",
        file_hash="dummyhashvalue",
        uploaded_by_user_id=user,
    )

    # Create a chunk associated with the file
    chunk = Chunk.objects.create(
        file=file,
        chunk_number=1,
        chunk_text="This is the text for chunk 1",
    )

    # Assert that the chunk is created successfully
    assert chunk.chunk_number == 1
    assert chunk.chunk_text == "This is the text for chunk 1"
    assert chunk.file == file  # The chunk is linked to the file


@pytest.mark.django_db
def test_embedding_creation():
    # Create a user (if needed)
    user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='password')

    # Create a file and chunk as needed (assuming chunk creation steps)
    file = File.objects.create(
        file_name="dummy_file.txt",
        s3_uri="https://s3.amazonaws.com/mybucket/dummy_file.txt",
        cdn_url="https://cdn.example.com/dummy_file.txt",
        file_hash="dummyhashvalue",
        uploaded_by_user_id=user,
    )

    chunk = Chunk.objects.create(
        file=file,
        chunk_number=1,
        chunk_text="This is the first chunk text",
    )

    # Create an embedding for the chunk
    embedding = Embedding.objects.create(
        embedding_id="embedding-uuid-1",
        vector=[0.5, 0.6, 0.7, 0.8],
        chunk=chunk,
    )

    # Assert that the embedding is created successfully and linked to the chunk
    assert embedding.embedding_id == "embedding-uuid-1"
    assert embedding.vector == [0.5, 0.6, 0.7, 0.8]
    assert embedding.chunk == chunk  # The embedding should be associated with the chunk
    assert embedding.created_at is not None  # created_at should be automatically set