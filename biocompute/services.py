#!/usr/bin/env python3
# biocopmute/services.py

import re
from urllib.parse import urlparse
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from biocompute.models import Bco
from prefix.models import Prefix
from prefix.services import prefix_counter_increment
from django.contrib.auth.models import Group, User
from rest_framework import serializers

"""BioCompute Services

Service functions for working with BCOs
"""

HOSTNAME = settings.PUBLIC_HOSTNAME

class BcoDraftSerializer(serializers.Serializer):
    object_id = serializers.URLField(required=False)
    contents = serializers.JSONField()
    prefix = serializers.CharField(max_length=5, min_length=3, default="BCO")
    authorized_groups = serializers.ListField(child=serializers.CharField(), required=False)
    authorized_users = serializers.ListField(child=serializers.CharField(), required=False)

    def validate(self, attrs):
        """BCO Draft Validator
        """

        errors = {}
        request = self.context.get('request')
        attrs["owner"] = request.user

        #check for groups
        if 'authorized_groups' in attrs:
            for group in attrs['authorized_groups']:
                try:
                    Group.objects.get(name=group)
                except Exception as err:
                    errors['authorized_groups'] = f"Invalid group: {group}"
        # check for users
        if 'authorized_users' in attrs:
            for user in attrs['authorized_users']:
                try:
                    # import pdb; pdb.set_trace()
                    User.objects.get(username=user)
                except Exception as err:
                    errors['authorized_users'] =f"Invalid user: {user}"

        # Validate Prefix
        try:
            #set a name and instance for Prefix
            attrs['prefix'] = Prefix.objects.get(prefix=attrs['prefix'])
            attrs['prefix_name'] = attrs['prefix'].prefix
        except Prefix.DoesNotExist as err:
            errors['prefix'] = 'Invalid prefix.'
            raise serializers.ValidationError(errors)

        # Validate or create object_id
        if 'object_id' in attrs:
            id_errors = validate_bco_object_id(
                attrs['object_id'],
                attrs['prefix_name']
            )
            if id_errors != 0:
                errors["object_id"] = id_errors
        else:
            attrs['object_id'] = create_bco_id(attrs['prefix'])

        # If erros exist than raise and exception and return it, otherwise
        # return validated data
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        # Remove the non-model field 'prefix_name' and use 'prefix' instance instead
        validated_data.pop('prefix_name')
        authorized_group_names = validated_data.pop('authorized_groups', [])
        authorized_usernames = validated_data.pop('authorized_users', [])
        bco_instance = Bco.objects.create(**validated_data, last_update=timezone.now())

        # Set ManyToMany relations
        if authorized_group_names:
            authorized_groups = Group.objects.filter(name__in=authorized_group_names)
            bco_instance.authorized_groups.set(authorized_groups)

        if authorized_usernames:
            authorized_users = User.objects.filter(username__in=authorized_usernames)
            bco_instance.authorized_users.set(authorized_users)

        return bco_instance


def validate_bco_object_id(object_id: str, prefix_name: str):
    """Validate BCO object ID

    Function to validate a proposed BCO object_id. Will reject the ID if the 
    following constraints are not met:
      1. Correct hostname for this BCODB instance
      2. Prefix submitted is not in the object_id
      3. The object_id already exists
    """
    errors = []
    
    if HOSTNAME not in object_id:
        errors.append("Object ID does not conform to the required format. "\
            + f"The hostname {HOSTNAME} is not in {object_id}")
    if prefix_name not in object_id:
        errors.append(f"Object ID, {object_id}, does not contain the "\
         + f"submitted prefix, {prefix_name}.")

    if not Bco.objects.filter(object_id=object_id).exists():
        pass
    else:
        errors.append(f"That object_id, {object_id}, already exists.")

    if errors:
        return errors
    return 0

def create_bco_id(prefix: Prefix) -> str:
    """Create BCO object_id

    Function to construct BCO object_id. Takes a Prefix model instance and 
    returns a bco.object_id.
    """

    count = prefix_counter_increment(prefix)
    bco_identifier = format(count, "06d")
    bco_id = f"{HOSTNAME}/{prefix}_{bco_identifier}/DRAFT"
    
    return bco_id
