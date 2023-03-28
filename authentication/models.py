import json
from django.db import models
from django.contrib.auth.models import User

class Authentication(models.Model):
    """"""
    username = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username")
    auth_service = models.JSONField(default=list)


    def __username__(self):
        """String for representing the model in Admin site."""
        return str(self.username)
