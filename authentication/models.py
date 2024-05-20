#!/usr/bin/env python3

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Authentication(models.Model):
    """Authentication Object
    """
    
    username = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username")
    auth_service = models.JSONField(default=list)

    def __username__(self):
        """String for representing the model in Admin site."""
        return str(self.username)

class NewUser(models.Model):
    """New User
    For registering new users.
    Instead of using the User model, just use
    a crude table to store the temporary information
    when someone asks for a new account."""

    email = models.EmailField()
    temp_identifier = models.TextField(max_length=100)
    token = models.TextField(blank=True, null=True)
    hostname = models.TextField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)