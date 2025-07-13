import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from users.models import File  # Import your File model

# Fixture: Reusable authenticated client
@pytest.fixture
def authenticated_client():
    client = APIClient()
    # Create and authenticate a test user
    user = get_user_model().objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    client.force_authenticate(user=user)
    return client

# Fixture: Test file data
@pytest.fixture
def test_file_data():
    return {
        'file_hash': 'a1b2c3d4e5f6g7h8i9j0',
        'file_name': 'test_document.pdf',
        's3_uri': 'https://s3.amazonaws.com/mybucket/test_document.pdf',
        'cdn_url': 'https://cdn.example.com/test_document.pdf'
    }

# Test 1: Successful presigned URL generation
@pytest.mark.django_db
def test_generate_presigned_url_success(authenticated_client, test_file_data):
    """
    Test successful generation of presigned URL with valid data
    """
    url = reverse('upload-request')
    
    response = authenticated_client.post(
        url,
        data=test_file_data,
        format='json'
    )
    
    # Assert response status
    assert response.status_code == 201
    
    # Assert response structure
    assert 'presigned_url' in response.data
    assert 'expiration' in response.data
    assert isinstance(response.data['presigned_url'], str)
    
    # Assert database record
    file_record = File.objects.first()  # Change this to the File model
    assert file_record.file_hash == test_file_data['file_hash']
    assert file_record.uploaded_by_user_id.username == 'testuser'  # User association in File model

# Test 2: Invalid data submission
@pytest.mark.django_db
def test_invalid_data(authenticated_client):
    """
    Test handling of invalid/missing parameters
    """
    url = reverse('upload-request')
    
    invalid_data = {
        'file_hash': 'invalid_short_hash',
        'file_name': '',
        's3_uri': 'https://s3.amazonaws.com/mybucket/test_document.pdf',  # Must provide all fields as per File model
        'cdn_url': 'https://cdn.example.com/test_document.pdf'
    }
    
    response = authenticated_client.post(
        url,
        data=invalid_data,
        format='json'
    )
    
    assert response.status_code == 400
    assert 'file_hash' in response.data
    assert 'file_name' in response.data

# Test 3: Duplicate file hash detection
@pytest.mark.django_db
def test_duplicate_file_hash(authenticated_client, test_file_data):
    """
    Test prevention of duplicate file uploads
    """
    url = reverse('upload-request')
    
    # First submission (should succeed)
    response1 = authenticated_client.post(url, test_file_data)
    assert response1.status_code == 201
    
    # Second submission (should fail)
    response2 = authenticated_client.post(url, test_file_data)
    assert response2.status_code == 400
    assert 'file_hash' in response2.data

# Test 4: Unauthorized access
@pytest.mark.django_db
def test_unauthenticated_access(test_file_data):
    """
    Test endpoint security with unauthenticated user
    """
    client = APIClient()  # Unauthenticated client
    url = reverse('upload-request')
    
    response = client.post(
        url,
        data=test_file_data,
        format='json'
    )
    
    assert response.status_code == 403
