import pytest
from django.contrib.auth import get_user_model
from datetime import datetime
from gmail_categorization_app.models import EmailMessage, UserGoogleAuth
from django.db import models 

@pytest.fixture
def email_data():
    return {
        'user_email': 'test@example.com',
        'subject': 'Test Subject',
        'body': 'Test email body content',
        'sentiment': 'positive'
    }

@pytest.fixture
def email_message(email_data):
    return EmailMessage.objects.create(**email_data)

@pytest.fixture
def test_user():
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123'
    )

@pytest.fixture
def user_google_auth(test_user):
    return UserGoogleAuth.objects.create(
        user=test_user,
        token=b'dummy_token_data'
    )

@pytest.mark.django_db
class TestEmailMessage:
    def test_email_creation(self, email_message, email_data):
        assert isinstance(email_message, EmailMessage)
        assert email_message.user_email == email_data['user_email']
        assert email_message.subject == email_data['subject']
        assert email_message.body == email_data['body']
        assert email_message.sentiment == email_data['sentiment']
        assert isinstance(email_message.received_at, datetime)

    def test_email_str_representation(self, email_message, email_data):
        assert str(email_message) == email_data['subject']

    def test_email_fields_max_length(self, email_message):
        max_length_subject = email_message._meta.get_field('subject').max_length
        max_length_email = email_message._meta.get_field('user_email').max_length
        assert max_length_subject == 255
        assert max_length_email == 254

@pytest.mark.django_db
class TestUserGoogleAuth:
    def test_google_auth_creation(self, user_google_auth, test_user):
        assert isinstance(user_google_auth, UserGoogleAuth)
        assert user_google_auth.user == test_user
        assert user_google_auth.token == b'dummy_token_data'
        assert isinstance(user_google_auth.created_at, datetime)
        assert isinstance(user_google_auth.updated_at, datetime)

    def test_google_auth_str_representation(self, user_google_auth):
        expected_str = f"Google Auth for {user_google_auth.user.username}"
        assert str(user_google_auth) == expected_str

    def test_one_to_one_relationship(self, user_google_auth):
        field = UserGoogleAuth._meta.get_field('user')
        assert field.one_to_one
        assert field.remote_field.on_delete == models.CASCADE

    def test_auto_timestamps(self, user_google_auth):
        assert user_google_auth.created_at is not None
        assert user_google_auth.updated_at is not None
        
        original_updated_at = user_google_auth.updated_at
        user_google_auth.token = b'new_token_data'
        user_google_auth.save()
        assert user_google_auth.updated_at != original_updated_at