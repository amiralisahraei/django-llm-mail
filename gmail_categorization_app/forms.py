from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))  # Add placeholder for username
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))  # Add placeholder for password1
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))  # Add placeholder for password2
    
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
        return user
