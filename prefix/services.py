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

        # Validate Prefix
        if not Prefix.objects.filter(prefix=prefix_name).exists():
            pass
        else:
            errors["prefix_name"] = f"That Prefix, {prefix_name}, already exists."
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
    

def prefix_counter_increment(prefix: Prefix) -> int:
    """Prefix Counter Increment 
    
    Simple incrementing function.
    Counter for BCO object_id asignment.
    """
    
    Prefix.objects.update(counter=F("counter") + 1)
    count = prefix.counter
    return count
