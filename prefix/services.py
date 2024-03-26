#!/usr/bin/env python3
# prefix/services.py

import re
from urllib.parse import urlparse
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from prefix.models import Prefix
from django.db import transaction
from django.contrib.auth.models import Group, User
from django.db.models import F
from rest_framework import serializers

"""Prefix Services

Service functions for working with BCO Prefixes
"""

class PrefixSerializer(serializers.Serializer):
    prefix = serializers.CharField(min_length=3, max_length=5)
    description = serializers.CharField()
    authorized_groups = serializers.ListField(child=serializers.CharField(allow_blank=True), required=False)
    public = serializers.BooleanField(required=False)
    
    def validate(self, attrs):
        """Prefix Validator
        """

        errors = {}
        request = self.context.get('request')
        attrs["owner"] = request.user
        attrs['prefix'] = attrs['prefix'].upper()
        prefix_name = attrs['prefix']

        # Validate Prefix name and owner
        try:
            attrs["prefix"] = Prefix.objects.get(prefix=prefix_name)
            if "create" in request.path_info:
                raise serializers.ValidationError({"prefix_name": f"That Prefix, {prefix_name}, already exists."})
            attrs["owner"] = attrs["prefix"].owner
        except Prefix.DoesNotExist:
            if "create" in request.path_info:
                pass
            else:
               raise serializers.ValidationError({"prefix_name": f"That Prefix, {prefix_name}, was not found."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create function for Prefix
        """
        public = validated_data.pop('public', [])
        import pdb; pdb.set_trace()
        prefix_instance = Prefix.objects.create(**validated_data, created=timezone.now())

        return prefix_instance

    @transaction.atomic
    def update(self, validated_data):
        """Update function for Prefix."""
        prefix_instance = Prefix.objects.get(prefix=validated_data['prefix'])
        if prefix_instance.owner != validated_data['owner']:
            return "denied"
        prefix_instance.description = validated_data.get('description', prefix_instance.description)
        prefix_instance.save()

        return prefix_instance

def create_permissions_for_prefix(instance=None, owner=User):
    """Prefix Permission Creation

    Creates permissions for a Prefix if it is not public. Owner is assigned
     all permissions and then can add permissions to other users.
    
	'view' -> View/download Prefix drafts
    'add' -> create new drafts for Prefix
	'change' -> Change existing drafts for Prefix
	'delete' -> Delete drafts for Prefix
	'publish' -> Publish drafts for Prefix
    """
    try:
        for perm in [ "view", "add", "change", "delete", "publish"]:
            print(instance)
            Permission.objects.create(
                name="Can " + perm + " BCOs with prefix " + instance.prefix,
                content_type=ContentType.objects.get(app_label="api", model="bco"),
                codename=perm + "_" + instance.prefix,)
    except:
        return 0

def prefix_counter_increment(prefix: Prefix) -> int:
    """Prefix Counter Increment 
    
    Simple incrementing function.
    Counter for BCO object_id asignment.
    """
    
    Prefix.objects.update(counter=F("counter") + 1)
    count = prefix.counter
    return count

def delete_prefix(prefix: str, user: User) -> bool:
    """Delete Prefix
    """
    try:
        prefix_instance = Prefix.objects.get(prefix=prefix)
    except Prefix.DoesNotExist:
        return f"That prefix, {prefix}, does not exist."
    if prefix_instance.owner == user:
        prefix_instance.delete()
        return True
    
    return f"You do not have permissions to delete that prefix, {prefix}."
