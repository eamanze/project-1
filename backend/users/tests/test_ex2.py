# backend/users/tests/test_models.py
import pytest
from django.contrib.auth import get_user_model

@pytest.fixture() # Arrange 
def user_1():
    CustomUser = get_user_model()
    print("Create user")
    return CustomUser.objects.create_user(
        email='test@test.com',
        username='test',
        password='testpassword'
    )
    
@pytest.mark.django_db
def test_check_password(user_1):
    print("set new password")
    user_1.set_password('newpassword') # Act
    print("check user and the new password")
    assert user_1.check_password('newpassword') is True # Assert 
    assert user_1.username == "test"