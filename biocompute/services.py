#!/usr/bin/env python3
# biocopmute/services.py

from django.db import transaction
from django.utils import timezone
from biocompute.models import Bco
from prefix.models import Prefix
from django.contrib.auth.models import Group, User
from rest_framework import serializers

"""BioCompute Services

Service functions for working with BCOs
"""

class BcoDraftSerializer(serializers.Serializer):
    object_id = serializers.URLField(required=False)
    contents = serializers.JSONField()
    prefix = serializers.CharField(max_length=5, min_length=3, default="BCO")
    authorized_groups = serializers.ListField(child=serializers.CharField(), required=False)
    authorized_users = serializers.ListField(child=serializers.CharField(), required=False)

    def validate(self, attrs):
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
            attrs['prefix_instance'] = Prefix.objects.get(prefix=attrs['prefix'])
        except Prefix.DoesNotExist as err:
            errors['prefix'] = 'Invalid prefix.'

        # Validate object_id match
        if 'object_id' in attrs and attrs['object_id'] != attrs['contents'].get('object_id', ''):
            errors["object_id"] = "object_id does not match object_id in contents."

        # Validate that object_id is unique
        object_id = attrs['contents'].get('object_id', '')
        
        if not Bco.objects.filter(object_id=object_id).exists():
            pass
        else:
            errors["object_id"] = f"That object_id, {attrs['object_id']}, already exists."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        # Remove the non-model field 'prefix' and use 'prefix_instance' instead
        prefix_instance = validated_data.pop('prefix_instance', None)
        validated_data.pop('prefix')
        authorized_group_names = validated_data.pop('authorized_groups', [])
        authorized_usernames = validated_data.pop('authorized_users', [])

        bco_instance = Bco.objects.create(**validated_data, prefix=prefix_instance, last_update=timezone.now())

        # Set ManyToMany relations
        if authorized_group_names:
            authorized_groups = Group.objects.filter(name__in=authorized_group_names)
            bco_instance.authorized_groups.set(authorized_groups)

        if authorized_usernames:
            authorized_users = User.objects.filter(username__in=authorized_usernames)
            bco_instance.authorized_users.set(authorized_users)

        return bco_instance
