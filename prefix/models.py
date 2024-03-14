from django.db import models
from django.contrib.auth.models import Group, User
from django.utils import timezone

class Prefix(models.Model):
    """
    """

    prefix = models.CharField(primary_key=True, max_length=5)
    certifying_key = models.TextField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username")
    authorized_groups = models.ManyToManyField(Group, blank=True, related_name='authorized_prefix')

    def __str__(self):
        """String for representing the BCO model (in Admin site etc.)."""
        return f"{self.prefix}"