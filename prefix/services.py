#!/usr/bin/env python3
# prefix/services.py

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, utils 
from django.db.models import F
from django.utils import timezone
from prefix.models import Prefix
from prefix.selectors import get_prefix_object, get_prefix_permissions
from rest_framework import serializers

"""Prefix Services

Service functions for working with BCO Prefixes
"""

class PrefixSerializer(serializers.Serializer):
    """Serializer for Prefix instances.

    For validation and serialization of Prefix data. 
    
    Fields:
    - prefix (CharField): 
        A unique identifier for the Prefix, with a length constraint between 3 to 5 characters. It is automatically converted to upper case.
    - description (CharField): 
        A textual description of the Prefix.
    - user_permissions (JSONField): 
        A JSON structure detailing specific user permissions related to the Prefix. This field is optional.
    - public (BooleanField): A flag indicating whether the Prefix is public or private. 
      This field is not required and defaults to `False` if not provided.

    Methods:
    - validate(self, attrs): Validates the Prefix data. 
    - create(self, validated_data): Creates a new Prefix instance from the validated data. 
    - update(self, instance, validated_data): Updates an existing Prefix instance based 
      on the validated data. 
    
    Note: The create and update operations are performed within a database transaction to 
    ensure data integrity.
    """

    prefix = serializers.CharField(min_length=3, max_length=5)
    description = serializers.CharField()
    user_permissions = serializers.JSONField(required=False, default={})
    public = serializers.BooleanField(required=False)
    
    def validate(self, attrs):
        """Prefix Validator

        Validates incoming Prefix data against business rules and integrity constraints.
        
        It ensures the prefix is unique (for creation), exists (for updates), and assigns
        the Prefix's owner based on the current request's user. It also converts the prefix
        to upper case for consistency.
        
        Parameters:
        - attrs (dict): The incoming Prefix data to validate.
        
        Returns:
        - dict: The validated Prefix data, potentially modified (e.g., upper-cased prefix).
        
        Raises:
        - serializers.ValidationError: If the prefix violates uniqueness or existence constraints.
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

        Creates a Prefix instance from the validated data.
        
        It handles the 'public' attribute specifically to manage permissions associated 
        with the Prefix. The 'user_permissions' field is ignored as it does not correspond 
        to a model field.
        
        Parameters:
        - validated_data (dict): The data that has passed validation checks.
        
        Returns:
        - Prefix: The newly created Prefix instance.
        """

        validated_data.pop('user_permissions')

        try: 
            public = validated_data['public']
        except KeyError:
            public, validated_data['public'] = True, True

        prefix_instance = Prefix.objects.create(**validated_data, created=timezone.now())
        
        if public is False:
            create_permissions_for_prefix(prefix_instance)
        prefix_instance.save()
        return prefix_instance

    @transaction.atomic
    def update(self, validated_data):
        """Update function for Prefix

        Updates an existing Prefix instance based on the validated data.
        
        It checks the ownership before applying changes, updates the Prefix's public status,
        and manages user permissions accordingly. 
        
        Parameters:
        - instance (Prefix): The Prefix instance to update.
        - validated_data (dict): The data that has passed validation checks.
        
        Returns:
        - Prefix: The updated Prefix instance.
        
        Raises:
        - PermissionError: If the current user does not own the Prefix.
        """

        prefix_instance = Prefix.objects.get(prefix=validated_data['prefix'])
        prefix_name = prefix_instance.prefix
        if prefix_instance.owner != validated_data['owner']:
            return "denied"
        if prefix_instance.public != validated_data['public']:
            #TODO: handle adding/deleting permissions for change of public status
            # add permissions to public -> private
            # Remove permissions to private -> public
            prefix_instance.public = validated_data['public']
        old_perms = get_prefix_permissions(prefix_name=prefix_name)
        if validated_data['user_permissions'] != old_perms:
            update_user_permissions(
                prefix_name= prefix_name,
                old_perms=old_perms,
                new_perms=validated_data['user_permissions']
            )
        
        prefix_instance.description = validated_data.get(
            'description', prefix_instance.description
        )
        prefix_instance.save()
        prefix_object = get_prefix_object(prefix_name)
        return prefix_object

def update_user_permissions(prefix_name:str, new_perms:dict, old_perms:dict):
    """
    Update user permissions based on a provided mapping of users to
    permissions. Only modifies permissions related to the specified prefix.

    Step 1: Build a list of permissions associated with the prefix
    Step 2: Iterate over users to update each user's permissions
    Step 3: Determine which permissions to add and which to remove
    Step 4: Apply permission updates
    """

    # Build a list of permissions associated with the prefix
    prefix_permissions = []
    for perm_type in ["view", "add", "change", "delete", "publish"]:
        codename = f"{perm_type}_{prefix_name}"
        try:
            perm = Permission.objects.get(codename=codename)
            prefix_permissions.append(perm)
        except Permission.DoesNotExist:
            pass

    prefix_permissions_dict = {perm.codename: perm for perm in prefix_permissions}

    # Set of all users mentioned in either new or old perms
    all_users = set(new_perms.keys()) | set(old_perms.keys())

    for username in all_users:
        try:
            user = User.objects.get(username=username)
            # Current permissions from old_perms or empty if not previously set
            current_perms = set(
                prefix_permissions_dict.get(perm_codename)
                for perm_codename in old_perms.get(username, [])
                if perm_codename in prefix_permissions_dict
            )
            
            # New permissions from new_perms or empty if not provided
            new_perms_set = set(
                prefix_permissions_dict.get(perm_codename)
                for perm_codename in new_perms.get(username, [])
                if perm_codename in prefix_permissions_dict
            )

            # Determine permissions to add and to remove
            perms_to_add = new_perms_set - current_perms
            perms_to_remove = current_perms - new_perms_set

            # Apply permission updates
            if perms_to_add:
                user.user_permissions.add(*perms_to_add)
            if perms_to_remove:
                user.user_permissions.remove(*perms_to_remove)

        except User.DoesNotExist:
            # Optionally handle the case where the user doesn't exist
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
    
    prefix_instance.counter = F('counter') + 1
    prefix_instance.save()

    prefix_instance.refresh_from_db()

    return prefix_instance.counter

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
