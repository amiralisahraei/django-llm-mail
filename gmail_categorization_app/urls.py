from django.urls import path
from .views import (
    main, signup, gmail_categorization,
    dashboard, login_view, gmail_auth, gmail_callback, upload_credentials
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', main, name='main'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', dashboard, name='user_profile'),
    path('gmail_categorization/', gmail_categorization, name='gmail_categorization'),
    path('gmail/auth/', gmail_auth, name='gmail_auth'),
    path('gmail/callback/', gmail_callback, name='gmail_callback'),
    path('upload-credentials/', upload_credentials, name='upload_credentials'),

]
