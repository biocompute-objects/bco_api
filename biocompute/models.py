#!/usr/bin/env python3
# biocompute/models.py

import sys
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.authtoken.models import Token
from prefix.models import Prefix

STATE_CHOICES = [
    ("REFERENCED", "referenced"),
    ("PUBLISHED", "published"),
    ("DRAFT", "draft"),
    ("DELETE", "delete")
]

class Bco(models.Model):
    """BioComput Object Model.

    Attributes:
    -----------
    object_id: str
        BCO Object Identifier, and primary key
    contents: JSONField
        BCO JSON contents
    authorized_group: ManyToManyField(Group)
        String representing the django.contrib.auth.models.Group that 'owns' the object
    owner_user = ForeignKey(User)
        String representing the django.contrib.auth.models.User that 'owns' the object
    prefix: str
        Prefix for the BCO
    state:str
        State of object. REFERENCED, PUBLISHED, DRAFT, and DELETE are currently accepted values.
    last_update: DateTime
        Date Time object for the last database change to this object

    """

    object_id = models.TextField(primary_key=True)
    contents = models.JSONField()
    prefix = models.ForeignKey(Prefix, on_delete=models.CASCADE, to_field="prefix")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE, 
        related_name="owned_bcos"
    )
    authorized_users = models.ManyToManyField(
        User, 
        related_name="authorized_bcos",
        blank=True
    )
    authorized_groups = models.ManyToManyField(Group,blank=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="DRAFT")
    last_update = models.DateTimeField()
    access_count = models.IntegerField(default=0)

    def __str__(self):
        """String for representing the BCO model (in Admin site etc.)."""
        return str(self.object_id)
