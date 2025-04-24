import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from django.contrib.messages import get_messages 

@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'testpass123',
        'password2': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
    }

@pytest.fixture
def user_data_login():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
    }

@pytest.fixture
def authenticated_client(client, django_user_model):
    user = django_user_model.objects.create_user(username='testuser', password='testpass123')
    client.login(username='testuser', password='testpass123')
    return client

@pytest.fixture
def mock_credentials_file():
    return SimpleUploadedFile(
        "credentials.json",
        b'{"web": {"client_id": "test", "client_secret": "test"}}',
        content_type="application/json"
    )

@pytest.mark.django_db
class TestMainViews:
    def test_main_page(self, client):
        response = client.get(reverse('main'))
        assert response.status_code == 200
        assert 'main.html' in [t.name for t in response.templates]

    def test_signup_get(self, client):
        response = client.get(reverse('signup'))
        assert response.status_code == 200
        assert 'registration/signup.html' in [t.name for t in response.templates]

    def test_signup_post_success(self, client, user_data):
        response = client.post(reverse('signup'), user_data)
        assert response.status_code == 302
        assert get_user_model().objects.filter(username=user_data['username']).exists()

    def test_signup_post_invalid(self, client):
        response = client.post(reverse('signup'), {})
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors


@pytest.mark.django_db
class TestAuthenticationViews:
    def test_login_get(self, client):
        response = client.get(reverse('login'))
        assert response.status_code == 200

    def test_login_post_success(self, client, user_data_login):
        get_user_model().objects.create_user(**user_data_login)
        response = client.post(reverse('login'), {
            'username': user_data_login['username'],
            'password': user_data_login['password']
        })
        assert response.status_code == 302
        assert response.url == reverse('user_profile')

    def test_login_post_invalid(self, client):
        response = client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': 'wrong'
        })
        messages = list(get_messages(response.wsgi_request))
        assert response.status_code == 200
        assert len(messages) > 0
        assert 'Username not found' in str(messages[0])


@pytest.mark.django_db
class TestDashboardViews:
    def test_dashboard_authenticated(self, authenticated_client):
        response = authenticated_client.get(reverse('user_profile'))
        assert response.status_code == 200
        assert 'emails' in response.context
        assert 'user_has_gmail_auth' in response.context

    def test_dashboard_unauthenticated(self, client):
        response = client.get(reverse('user_profile'))
        assert response.status_code == 302
        assert reverse('login') in response.url


@pytest.mark.django_db
class TestGmailViews:
    @patch('gmail_categorization_app.views.categorize_main')
    def test_gmail_categorization_authenticated(self, mock_categorize, authenticated_client):
        response = authenticated_client.get(reverse('gmail_categorization'))
        assert response.status_code == 302
        assert reverse('upload_credentials') in response.url

    def test_upload_credentials_get(self, authenticated_client):
        response = authenticated_client.get(reverse('upload_credentials'))
        assert response.status_code == 200

    def test_upload_credentials_post_success(self, authenticated_client, mock_credentials_file):
        response = authenticated_client.post(reverse('upload_credentials'), {
            'credentials': mock_credentials_file
        })
        assert response.status_code == 302
        assert reverse('gmail_auth') in response.url

    def test_upload_credentials_post_invalid(self, authenticated_client):
        invalid_file = SimpleUploadedFile("credentials.txt", b"invalid", content_type="text/plain")
        response = authenticated_client.post(reverse('upload_credentials'), {
            'credentials': invalid_file
        })
        assert response.status_code == 200
        assert 'error' in [m.level_tag for m in response.context['messages']]


@pytest.mark.django_db
class TestGmailAuthFlow:
    def test_gmail_auth_with_credentials(self, authenticated_client):
        session = authenticated_client.session
        session['temp_credentials_path'] = '/tmp/test_creds.json'
        session.save()

        with patch('gmail_categorization_app.views.Flow') as mock_flow:
            mock_flow_instance = MagicMock()
            mock_flow_instance.authorization_url.return_value = ('http://auth_url', 'test_state')
            mock_flow.from_client_secrets_file.return_value = mock_flow_instance

            response = authenticated_client.get(reverse('gmail_auth'))

            assert response.status_code == 302
            assert response.url == 'http://auth_url'
            assert authenticated_client.session['gmail_auth_state'] == 'test_state'

    def test_gmail_auth_without_credentials(self, authenticated_client):
        response = authenticated_client.get(reverse('gmail_auth'))
        assert response.status_code == 302
        assert reverse('upload_credentials') in response.url
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'Please upload your credentials.json file first' in str(messages[0])
