from django.contrib import admin
from django.db import models
from .models import EmailMessage

@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'subject', 'sentiment', 'received_at')
    search_fields = ('user_email', 'subject', 'body')
