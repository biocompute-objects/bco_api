#!/usr/bin/env python3
# biocopmute/services.py

from biocompute.models import Bco
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from prefix.models import Prefix
from prefix.services import prefix_counter_increment
from rest_framework import serializers

"""BioCompute Services

Service functions for working with BCOs
"""

HOSTNAME = settings.PUBLIC_HOSTNAME

class BcoDraftSerializer(serializers.Serializer):
    """Serializer for drafting BioCompute Objects (BCO).

    This serializer is used to validate and serialize data related to the
    creation or update of BCO drafts. It handles the initial data validation
    including the existence of users specified as authorized users, the
    validity of the prefix, and the construction or validation of the object_id
    if provided.

    Attributes:
    - object_id (URLField, optional): 
        The unique identifier of the BCO, which should be a URL. This field is
        not required for creation as it can be generated.
    - contents (JSONField): 
        The contents of the BCO in JSON format.
    - prefix (CharField): 
        A short alphanumeric prefix related to the BCO. Defaults to 'BCO'.
    - authorized_users (ListField): 
        A list of usernames authorized to access the BCO, besides the owner.

    Methods:
    - validate: Validates the incoming data for creating or updating a BCO draft.
    - create: Creates a new BCO instance based on the validated data.
    """

    object_id = serializers.URLField(required=False)
    contents = serializers.JSONField()
    prefix = serializers.CharField(max_length=5, min_length=3, default="BCO")
    authorized_users = serializers.ListField(child=serializers.CharField(), required=False)

    def validate(self, attrs):
        """BCO Draft Validator

        Validates the presence and correctness of 'authorized_users' and
        'prefix'. If 'object_id' is provided, it validates the format and 
        uniqueness of it. Adds the request's user as the owner of the BCO.

        Parameters:
        - attrs (dict): The incoming data to be validated.

        Returns:
        - dict: The validated data with additional fields such as 'owner' and
        potentially modified 'prefix'.

        Raises:
        - serializers.ValidationError: If any validation checks fail.
        """

        errors = {}
        request = self.context.get('request')
        attrs["owner"] = request.user

        if 'authorized_users' in attrs:
            for user in attrs['authorized_users']:
                try:
                    User.objects.get(username=user)
                except Exception as err:
                    errors['authorized_users'] =f"Invalid user: {user}"

        try:
            attrs['prefix'] = Prefix.objects.get(prefix=attrs['prefix'])
            attrs['prefix_name'] = attrs['prefix'].prefix
        except Prefix.DoesNotExist as err:
            errors['prefix'] = 'Invalid prefix.'
            raise serializers.ValidationError(errors)

        if 'object_id' in attrs:
            id_errors = validate_bco_object_id(
                attrs['object_id'],
                attrs['prefix_name']
            )
            if id_errors != 0:
                errors["object_id"] = id_errors

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Creates a new BCO instance based on the validated data.

        If 'object_id' is not provided in the validated data, it generates one.
        It also handles the creation of the BCO instance and setting up the
        many-to-many relationships for 'authorized_users'.

        Parameters:
        - validated_data (dict): The validated data used to create the BCO.

        Returns:
        - Bco: The newly created Bco instance.
        """

        validated_data.pop('prefix_name')
        authorized_usernames = validated_data.pop('authorized_users', [])
        if 'object_id' not in validated_data:
            validated_data['object_id'] = create_bco_id(
                validated_data['prefix']
            )
        bco_instance = Bco.objects.create(
            **validated_data, last_update=timezone.now()
        )

        if authorized_usernames:
            authorized_users = User.objects.filter(
                username__in=authorized_usernames
            )
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

def create_bco_id(prefix_instance: Prefix) -> str:
    """Create BCO object_id

    Constructs a BCO object_id using a Prefix model instance.
    Ensures uniqueness by incrementing the prefix's counter until a unique ID
    is found.
    """

    unique_id_found = False
    
    while not unique_id_found:
        count = prefix_counter_increment(prefix_instance)
        bco_identifier = format(count, "06d")
        bco_id = f"{HOSTNAME}/{prefix_instance.prefix}_{bco_identifier}/DRAFT"

        if not Bco.objects.filter(object_id=bco_id).exists():
            unique_id_found = True
    
    return bco_id

def bco_counter_increment(bco_instance: Bco) -> int:
    """BCO Counter Increment 
    
    Simple incrementing function.
    Counter for BCO object_id asignment.
    """
    
    bco_instance.access_count = F('access_count') + 1
    bco_instance.save()

    bco_instance.refresh_from_db()

    return bco_instance.access_count