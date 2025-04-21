from django.contrib import admin
from django.db import models
from .models import EmailMessage
from .models import UserGoogleAuth

@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'subject', 'sentiment', 'received_at')
    search_fields = ('user_email', 'subject', 'body')


@admin.register(UserGoogleAuth)
class UserGoogleAuthAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)