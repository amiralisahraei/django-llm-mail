from django.db import models
from django.conf import settings

class EmailMessage(models.Model):
    user_email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sentiment = models.CharField(max_length=50, null=True)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
    

class UserGoogleAuth(models.Model):
    """Store user-specific Google authentication credentials"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.BinaryField()  # To store the pickled credentials
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Google Auth for {self.user.username}"