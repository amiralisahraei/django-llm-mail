from django.urls import path
from .views import main, signup, gmail_categorization, dashboard, login_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', main, name='main'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', dashboard, name='user_profile'),
    path('gmail_categorization/', gmail_categorization, name='gmail_categorization'),
]
