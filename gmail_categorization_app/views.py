import os
import pickle
import tempfile
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from google_auth_oauthlib.flow import Flow
from django.urls import reverse
from .forms import CustomUserCreationForm
from .models import EmailMessage, UserGoogleAuth
from django.utils import timezone
from google.auth.transport.requests import Request
import logging
from gmail_categorization_app.categorization.app import main as categorize_main

logger = logging.getLogger(__name__)


def main(request):
    """Render the main page."""
    return render(request, 'main.html')


def login_view(request):
    """Handle user login with specific error messages."""
    username = ''
    form = AuthenticationForm()

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            if not username and not password:
                messages.error(request, 'Please enter both username and password.')
            elif not username:
                messages.error(request, 'Please enter your username.')
            else:
                messages.error(request, 'Please enter your password.')
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('user_profile')
            else:
                user_exists = get_user_model().objects.filter(username=username).exists()
                if user_exists:
                    messages.error(request, 'Incorrect password. Please try again.')
                else:
                    messages.error(request, 'Username not found. Please check your username or sign up.')

    return render(request, 'registration/login.html', {'form': form, 'username': username})


def signup(request):
    """Handle user sign-up with email field."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required(login_url='login')
def dashboard(request):
    """Render the dashboard with user profile info and email list."""
    emails = EmailMessage.objects.filter(user_email=request.user.email).order_by('received_at')
    user_has_gmail_auth = UserGoogleAuth.objects.filter(user=request.user).exists()
    context = {
        'user': request.user,
        'emails': emails,
        'user_has_gmail_auth': user_has_gmail_auth
    }
    return render(request, 'user_profile.html', context)


@login_required(login_url='login')
def gmail_categorization(request):
    """Render the Gmail categorization page and redirect to dashboard."""
    try:
        if not UserGoogleAuth.objects.filter(user=request.user).exists():
            messages.error(request, 'Please authenticate with Gmail first')
            return redirect('upload_credentials')

        categorize_main(request.user)
        messages.success(request, 'Emails synchronized successfully')
    except Exception as e:
        messages.error(request, f'Error synchronizing emails: {str(e)}')
        logger.error(f'Gmail categorization error for user {request.user}: {str(e)}')
    return redirect('user_profile')


@login_required
def upload_credentials(request):
    """Handle temporary upload of credentials.json file."""
    if request.method == 'POST':
        credentials_file = request.FILES.get('credentials')
        if not credentials_file:
            messages.error(request, 'Please select a credentials file')
            return redirect('user_profile')

        if not credentials_file.name.endswith('.json'):
            messages.error(request, 'Please upload a valid credentials.json file')
            return redirect('user_profile')

        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in credentials_file.chunks():
                    temp_file.write(chunk)

            request.session['temp_credentials_path'] = temp_file.name
            return redirect('gmail_auth')
        except Exception as e:
            messages.error(request, f'Error processing credentials file: {str(e)}')
            return redirect('user_profile')

    return render(request, 'upload_credentials.html')


@login_required
def gmail_auth(request):
    """Handle Gmail authentication for each user."""
    try:
        temp_credentials_path = request.session.get('temp_credentials_path')
        if not temp_credentials_path:
            messages.error(request, 'Please upload your credentials.json file first')
            return redirect('upload_credentials')

        user_auth = UserGoogleAuth.objects.filter(user=request.user).first()
        if user_auth:
            try:
                credentials = pickle.loads(user_auth.token)
                if credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                    user_auth.token = pickle.dumps(credentials)
                    user_auth.save()
                elif not credentials.expired:
                    messages.success(request, 'Already authenticated with Gmail')
                return redirect('user_profile')
            except Exception:
                user_auth.delete()

        flow = Flow.from_client_secrets_file(
            temp_credentials_path,
            scopes=['https://www.googleapis.com/auth/gmail.readonly', 
                    'https://www.googleapis.com/auth/gmail.modify'],
            redirect_uri=request.build_absolute_uri(reverse('gmail_callback'))
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        request.session['gmail_auth_state'] = state
        return redirect(authorization_url)
    except Exception as e:
        _cleanup_temp_file(request)
        messages.error(request, f'Gmail authentication failed: {str(e)}')
        logger.error(f'Gmail auth error for user {request.user}: {str(e)}')
        return redirect('user_profile')


@login_required
def gmail_callback(request):
    """Handle the OAuth2 callback from Google."""
    try:
        temp_credentials_path = request.session.get('temp_credentials_path')
        if not temp_credentials_path:
            raise ValueError('Credentials file not found. Please upload again.')

        stored_state = request.session.pop('gmail_auth_state', None)
        if stored_state != request.GET.get('state'):
            raise ValueError('Invalid state parameter')

        if 'error' in request.GET:
            raise ValueError(f'Authorization failed: {request.GET.get("error")}')

        flow = Flow.from_client_secrets_file(
            temp_credentials_path,
            scopes=['https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/gmail.modify'],
            state=stored_state,
            redirect_uri=request.build_absolute_uri(reverse('gmail_callback'))
        )
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials

        if not credentials or not credentials.valid:
            raise ValueError('Failed to obtain valid credentials')

        UserGoogleAuth.objects.update_or_create(
            user=request.user,
            defaults={
                'token': pickle.dumps(credentials),
                'updated_at': timezone.now()
            }
        )
        _cleanup_temp_file(request)
        messages.success(request, 'Successfully authenticated with Gmail')
    except Exception as e:
        _cleanup_temp_file(request)
        messages.error(request, f'Authentication failed: {str(e)}')
        logger.error(f'Gmail callback error for user {request.user}: {str(e)}')
    return redirect('user_profile')


def _cleanup_temp_file(request):
    """Helper function to clean up temporary credentials file."""
    temp_credentials_path = request.session.pop('temp_credentials_path', None)
    if temp_credentials_path and os.path.exists(temp_credentials_path):
        os.unlink(temp_credentials_path)
