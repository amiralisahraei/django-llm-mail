from django.db import models

class EmailMessage(models.Model):
    user_email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sentiment = models.CharField(max_length=50, null=True)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject