#!/usr/bin/env python3
# prefix/services.py

import re
from urllib.parse import urlparse
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import utils 
from django.utils import timezone
from prefix.models import Prefix
from django.db import transaction
from django.contrib.auth.models import User
from django.db.models import F
from rest_framework import serializers
from prefix.selectors import get_prefix_permissions, get_prefix_object

"""Prefix Services

Service functions for working with BCO Prefixes
"""

class PrefixSerializer(serializers.Serializer):
    prefix = serializers.CharField(min_length=3, max_length=5)
    description = serializers.CharField()
    authorized_groups = serializers.ListField(child=serializers.CharField(allow_blank=True), required=False)
    user_permissions = serializers.JSONField(required=False, default={})
    public = serializers.BooleanField(required=False)
    
    def validate(self, attrs):
        """Prefix Validator
        """

        request = self.context.get('request')
        attrs["owner"] = request.user
        attrs['prefix'] = attrs['prefix'].upper()
        prefix_name = attrs['prefix']

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

        validated_data.pop('user_permissions')
        public = validated_data['public']
        prefix_instance = Prefix.objects.create(**validated_data, created=timezone.now())
        
        if public is False:
            create_permissions_for_prefix(prefix_instance)
        prefix_instance.save()
        return prefix_instance

    @transaction.atomic
    def update(self, validated_data):
        """Update function for Prefix

        """

        prefix_instance = Prefix.objects.get(prefix=validated_data['prefix'])
        prefix_name = prefix_instance.prefix
        if prefix_instance.owner != validated_data['owner']:
            return "denied"
        if prefix_instance.public != validated_data['public']:
            prefix_instance.public = validated_data['public']
            #TODO: handle adding/deleting permissions for change of public status
        update_user_permissions(prefix_name,validated_data['user_permissions'])
        prefix_instance.description = validated_data.get('description', prefix_instance.description)
        prefix_instance.save()
        prefix_object = get_prefix_object(prefix_name)
        return prefix_object

def update_user_permissions(prefix_name: str, user_permissions: dict):
    """Udate Prefix Permissions

    Update user permissions based on a provided mapping of users to permissions.
    Only modifies permissions related to the specified prefix.
    Step 1: Build a list of permissions associated with the prefix
    Step 2: Iterate over the user_permissions dict to update each user
    Step 3: Find which permissions to add (from the provided list) and which to remove
    Step 4: Add new permissions and remove old ones not in the new list
    """

    prefix_permissions = []
    for perm_type in ["view", "add", "change", "delete", "publish"]:
        codename = f"{perm_type}_{prefix_name}"
        try:
            perm = Permission.objects.get(codename=codename)
            prefix_permissions.append(perm)
        except Permission.DoesNotExist:
            # If the permission doesn't exist, skip it
            pass

    prefix_permissions_dict = {
        perm.codename: perm for perm in prefix_permissions
    }

    for username, perms in user_permissions.items():
        try:
            user = User.objects.get(username=username)
            current_perms = set(user.user_permissions.filter(
                pk__in=[permission.pk for permission in prefix_permissions])
            )
            new_perms = {
                prefix_permissions_dict[perm_codename] for perm_codename \
                in perms if perm_codename in prefix_permissions_dict
            }

            perms_to_add = new_perms - current_perms
            perms_to_remove = current_perms - new_perms

            if perms_to_add:
                user.user_permissions.add(*perms_to_add)
            if perms_to_remove:
                user.user_permissions.remove(*perms_to_remove)

        except User.DoesNotExist:
            # Handle case where user doesn't exist if necessary
            pass


def create_permissions_for_prefix(instance=Prefix):
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
            new_perm = Permission.objects.create(
                name="Can " + perm + " BCOs with prefix " + instance.prefix,
                content_type=ContentType.objects.get(app_label="prefix", model="prefix"),
                codename=perm + "_" + instance.prefix,)
            instance.owner.user_permissions.add(new_perm)

    except utils.IntegrityError:
        # The permissions already exist.
        pass

def prefix_counter_increment(prefix_instance: Prefix) -> int:
    """Prefix Counter Increment 
    
    Simple incrementing function.
    Counter for BCO object_id asignment.
    """
    
    Prefix.objects.update(counter=F("counter") + 1)
    count = prefix_instance.counter
    return count

@transaction.atomic
def delete_prefix(prefix_name: str, user: User) -> bool:
    """Delete Prefix

    Deletes a prefix and the permissions.
    `view` and `delete` permissions are not removed so that existing BCOs can
    still be viewed or individually removed.
    
    'add' -> create new drafts for Prefix
	'change' -> Change existing drafts for Prefix
	'publish' -> Publish drafts for Prefix
    """

    try:
        prefix_instance = Prefix.objects.get(prefix=prefix_name)
    except Prefix.DoesNotExist:
        return f"That prefix, {prefix_name}, does not exist."

    if prefix_instance.owner == user:
        prefix_instance.delete()
        if prefix_instance.public is False:
            for perm in ["add", "change",  "publish"]:
                try:
                    Permission.objects.get(codename=f"{perm}_{prefix_name}").delete()
                    print(f"{perm}_{prefix_name}")
                except Permission.DoesNotExist:
                    pass
        return True
    
    return f"You do not have permissions to delete that prefix, {prefix_name}."
