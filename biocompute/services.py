#!/usr/bin/env python3
# biocopmute/services.py

import json
from hashlib import sha256
from biocompute.models import Bco
from copy import deepcopy
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

class ModifyBcoDraftSerializer(serializers.Serializer):
    """Serializer for modifying draft BioCompute Objects (BCO).

    This serializer is used to validate and serialize data related to the
    update of BCO drafts.

    Attributes:
    - contents (JSONField): 
        The contents of the BCO in JSON format.
    - authorized_users (ListField): 
        A list of usernames authorized to access the BCO, besides the owner.

    Methods:
    - validate: Validates the incoming data for updating a BCO draft.
    - update: Updates a BCO instance based on the validated data.
    """
    contents = serializers.JSONField()
    authorized_users = serializers.ListField(child=serializers.CharField(), required=False)

    def validate(self, attrs):
        """BCO Modify Draft Validator

        Parameters:
        - attrs (dict): 
            The incoming data to be validated.

        Returns:
        - dict:
            The validated data.

        Raises:
        - serializers.ValidationError: If any validation checks fail.
        """

        errors = {}
        request = self.context.get('request')

        if 'authorized_users' in attrs:
            for user in attrs['authorized_users']:
                try:
                    User.objects.get(username=user)
                except Exception as err:
                    errors['authorized_users'] =f"Invalid user: {user}"

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    @transaction.atomic
    def update(self, validated_data):
        """
        """

        authorized_usernames = validated_data.pop('authorized_users', [])
        bco_instance = Bco.objects.get(
            object_id = validated_data['contents']['object_id']
        )
        bco_instance.contents = validated_data['contents']
        bco_instance.last_update=timezone.now()
        bco_contents = deepcopy(bco_instance.contents)
        etag = generate_etag(bco_contents)
        bco_instance.contents['etag'] = etag
        bco_instance.save()
        if authorized_usernames:
            authorized_users = User.objects.filter(
                username__in=authorized_usernames
            )
            bco_instance.authorized_users.set(authorized_users)

        return bco_instance

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
        The `etag` is then generated after the BCO is created. 
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
            object_id = create_bco_id(validated_data['prefix'])
            validated_data['object_id'] = object_id
            validated_data['contents']['object_id'] = object_id

        
        bco_instance = Bco.objects.create(
            **validated_data, last_update=timezone.now()
        )
        bco_contents = deepcopy(bco_instance.contents)
        etag = generate_etag(bco_contents)
        bco_instance.contents['etag'] = etag
        bco_instance.save()

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
    
    Increments the access count for a BioCompute Object (BCO).

    This function is designed to track the number of times a specific BCO has
    been accessed or viewed. It increments the `access_count` field of the
    provided BCO instance by one and saves the update to the database.

    Parameters:
    - bco_instance (Bco):
        An instance of the BCO model whose access count is to be incremented.

    Returns:
    - int:
        The updated access count of the BCO instance after incrementing.
    """
    
    bco_instance.access_count = F('access_count') + 1
    bco_instance.save()

    bco_instance.refresh_from_db()

    return bco_instance.access_count

def generate_etag(bco_contents: dict) -> str:
    """Genreate ETag

    Generates a SHA-256 hash etag for a BioCompute Object (BCO).

    The etag serves as a string-type, read-only value that protects the BCO
    from internal or external alterations without proper validation. It is
    generated by hashing the contents of the BCO using the SHA-256 hash
    function. To ensure the integrity and uniqueness of the etag, the
    'object_id', 'spec_version', and 'etag' fields are excluded from the hash
    generation process.

    Parameters:
    - bco_contents (dict):
        The contents of the BCO, from which the etag will be generated.

    Returns:
    - str: 
        A SHA-256 hash string acting as the etag for the BCO.
    """

    del bco_contents['object_id'], bco_contents['spec_version'], bco_contents['etag']
    bco_etag = sha256(json.dumps(bco_contents).encode('utf-8')).hexdigest()
    return bco_etag
