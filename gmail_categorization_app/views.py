from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from .models import EmailMessage
from gmail_categorization_app.categorization.app import main as categorize_main

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

        # Field validation - check empty fields first
        if not username or not password:
            if not username and not password:
                messages.error(request, 'Please enter both username and password.')
            elif not username:
                messages.error(request, 'Please enter your username.')
            else:
                messages.error(request, 'Please enter your password.')

        else:
            # Authenticate user only if both fields are provided
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_profile')
            else:
                # Check if user exists
                User = get_user_model()
                user_exists = User.objects.filter(username=username).exists()
                if user_exists:
                    messages.error(request, 'Incorrect password. Please try again.')
                else:
                    messages.error(request, 'Username not found. Please check your username or sign up.')

    return render(request, 'registration/login.html', {
        'form': form,
        'username': username,
    })

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
    """Render the merged dashboard with user profile info and email list."""
    user_email = request.user.email
    emails = EmailMessage.objects.filter(user_email=user_email).order_by('-received_at')
    return render(request, 'user_profile.html', {'user': request.user, 'emails': emails})

@login_required(login_url='login')
def gmail_categorization(request):
    """Render the Gmail categorization page and redirect to dashboard."""
    user_email = request.user.email
    categorize_main(user_email)
    return redirect('user_profile')
