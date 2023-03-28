#!/usr/bin/env python3
"""Models

Explanation of optional fields: 
https://stackoverflow.com/questions/16349545/optional-fields-in-django-models
TextField is used here because it has no character limit.

Create a base model, then inherit for each table.
See the 4th example under "Model Inheritance" at 
https://docs.djangoproject.com/en/3.1/topics/db/models/#model-inheritance

--- Permissions imports --- #
Source: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
For setting the anonymous key.
The user model is straight from Django.
Referencing models.
Issue with timezones.
Source: https://stackoverflow.com/a/32411560
Object-level permissions.
For token creation.
Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.authtoken.models import Token


# Generic BCO model
class BCO(models.Model):
    """BioComput Object Model.

    Attributes:
    -----------
    contents: JSONField
        BCO JSON contents
    object_class: str
        T.B.D.
    object_id: str
        BCO Object Identifier
    owner_group: str
        String representing the django.contrib.auth.models.Group that 'owns' the object
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username')
        String representing the django.contrib.auth.models.User that 'owns' the object
    prefix: str
        Prefix for the BCO
    schema: str
        schema to which the BCO should be validated. Default is 'IEEE'
    state:str
        State of object. REFERENCED, PUBLISHED, DRAFT, and DELETE are currently accepted values.
    last_update: DateTime
        Date Time object for the last database change to this object
    """

    contents = models.JSONField()
    object_class = models.TextField(blank=True, null=True)
    object_id = models.TextField()
    owner_group = models.ForeignKey(Group, on_delete=models.CASCADE, to_field="name")
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username")
    prefix = models.CharField(max_length=5)
    schema = models.TextField()
    state = models.TextField()
    last_update = models.DateTimeField()

    def __str__(self):
        """String for representing the BCO model (in Admin site etc.)."""
        return str(self.object_id)


# For registering new users.
class new_users(models.Model):
    """Instead of using the User model, just use
    a crude table to store the temporary information
    when someone asks for a new account."""

    email = models.EmailField()
    temp_identifier = models.TextField(max_length=100)
    # In case we are writing back to UserDB.
    token = models.TextField(blank=True, null=True)

    # Which host to send the activation back to (i.e. UserDB).
    hostname = models.TextField(blank=True, null=True)
    # Issue with time zone, so implement the fix.
    # Source: https://stackoverflow.com/a/32411560
    created = models.DateTimeField(default=timezone.now)

    def __email__(self):
        return str(self.email)

    def __token__(self):
        return str(self.token)

    def __hostname__(self):
        return str(self.hostname)

    def __temp_identifier__(self):
        return str(self.temp_identifier)


# def get_first_name(self):
#     return self.first_name

# User.add_to_class("__str__", get_first_name)


# --- Receivers --- #


# User and API Information are kept separate so that we can use it
# elsewhere easily.

# Source: https://florimondmanca.github.io/djangorestframework-api-key/guide/#api-key-models
# Source: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html


# --- User --- #


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Link user creation to token generation.
    Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
    """
    if created:
        # The anonymous user's token is hard-coded
        # in server.conf.
        if instance.username == "anon":
            # Create anon's record with the hard-coded key.
            Token.objects.create(user=instance, key=settings.ANON_KEY)
        else:
            # Create a normal user's record.
            Token.objects.create(user=instance)


# Link object deletion to object permissions deletion.

# TODO:...
