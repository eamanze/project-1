# backend/users/tests/test_models.py
import pytest
from django.contrib.auth import get_user_model

@pytest.mark.django_db
def test_custom_user_creation():
    CustomUser = get_user_model()
    
    # Use the manager's create_user method correctly
    user = CustomUser.objects.create_user(
        email='test@test.com',
        username='test',
        password='testpassword'
    )
    
    assert CustomUser.objects.count() == 1
    assert user.email == 'test@test.com'
    assert user.username == 'test'
    assert user.check_password('testpassword')  # Verify hashing
    
    # Test invalid creation
    with pytest.raises(ValueError):
        CustomUser.objects.create_user(
            email='',
            username='invalid',
            password='testpassword'
        )