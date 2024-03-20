#!/usr/bin/env python3
# prefix/services.py

import re
from urllib.parse import urlparse
from django.conf import settings
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
                errors["prefix_name"] = f"That Prefix, {prefix_name}, was not found."



        # remove blank 'authorized_groups' relic from legacy conversion
        if attrs['authorized_groups'][0] == "":
            attrs.pop("authorized_groups")

        #check for groups
        if 'authorized_groups' in attrs:
            for group in attrs['authorized_groups']:
                try:
                    Group.objects.get(name=group)
                except Group.DoesNotExist as err:
                    errors['authorized_groups'] = f"Invalid group: {group}"

        # If erros exist than raise and exception and return it, otherwise
        # return validated data
        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create function for Prefix
        """
        authorized_group_names = validated_data.pop('authorized_groups', [])
        prefix_instance = Prefix.objects.create(**validated_data, created=timezone.now())
        # Set ManyToMany relations
        if authorized_group_names:
            authorized_groups = Group.objects.filter(name__in=authorized_group_names)
            prefix_instance.authorized_groups.set(authorized_groups)
        return prefix_instance

    @transaction.atomic
    def update(self, validated_data):
        """Update function for Prefix."""
        prefix_instance = Prefix.objects.get(prefix=validated_data['prefix'])
        if prefix_instance.owner != validated_data['owner']:
            # import pdb; pdb.set_trace()
            return "denied"
        prefix_instance.description = validated_data.get('description', prefix_instance.description)
        prefix_instance.save()

        if 'authorized_groups' in validated_data:
            authorized_group_names = validated_data['authorized_groups']
            # If the list is empty or contains only an empty string, clear the groups
            if not authorized_group_names or authorized_group_names == [""]:
                prefix_instance.authorized_groups.clear()

            else:
                # Filter groups that exist in the database
                authorized_groups = Group.objects.filter(name__in=authorized_group_names)
                
                # Set the new groups, which automatically handles adding, keeping, or removing
                prefix_instance.authorized_groups.set(authorized_groups)

        return prefix_instance

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
