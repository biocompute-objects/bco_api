#!/usr/bin/env python3
# biocopmute/services.py

import copy
import json
import jsonref
import jsonschema
import re
from hashlib import sha256
from biocompute.models import Bco
from biocompute.selectors import object_id_deconstructor, datetime_converter
from copy import deepcopy
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from prefix.models import Prefix
from prefix.services import prefix_counter_increment
from rest_framework import serializers
from simplejson.errors import JSONDecodeError
from requests.exceptions import ConnectionError as RequestsConnectionError

"""BioCompute Services

Service functions for working with BCOs
"""

HOSTNAME = settings.PUBLIC_HOSTNAME
BASE_DIR = settings.BASE_DIR

class BcoValidator:
    """BCO Validator

    Handles validation of BioCompute Objects (BCOs) against JSON Schemas.
    """

    def __init__(self):
        """Initializes the BCOValidator with common attributes, if any."""
        self.base_path = f"{BASE_DIR}/config/IEEE/2791object.json"

    @staticmethod
    def load_schema(schema_uri):
        """
        Loads a JSON Schema from a given URI.

        Parameters:
        - schema_uri (str): The URI or path to the JSON schema.

        Returns:
        - dict: The loaded JSON schema.
        """
        schema_mapping = {
            "https://w3id.org/ieee/ieee-2791-schema/2791object.json": f"{BASE_DIR}/config/schemas/2791object.json",
            "https://raw.githubusercontent.com/biocompute-objects/extension_domain/1.1.0/dataset_extension.json": f"{BASE_DIR}/config/schemas/dataset_extension.json",
            "https://raw.githubusercontent.com/biocompute-objects/extension_domain/1.1.0/fhir_extension.json": f"{BASE_DIR}/config/schemas/fhir_extension.json",
            "https://raw.githubusercontent.com/biocompute-objects/extension_domain/1.1.0/galaxy_extension.json": f"{BASE_DIR}/config/schemas/galaxy_extension.json",
            "https://raw.githubusercontent.com/biocompute-objects/extension_domain/1.1.0/license_extension.json": f"{BASE_DIR}/config/schemas/license_extension.json",
            "https://raw.githubusercontent.com/biocompute-objects/extension_domain/1.1.0/scm_extension.json": f"{BASE_DIR}/config/schemas/scm_extension.json"
        }
        if schema_uri in schema_mapping:
            return jsonref.load_uri(f"file://{schema_mapping[schema_uri]}")
        try:
            return jsonref.load_uri(schema_uri)
        except (JSONDecodeError, TypeError, RequestsConnectionError) as e:
            error_msg = "Failed to load schema. "
            if isinstance(e, JSONDecodeError):
                return {schema_uri: [error_msg + "JSON Decode Error."]}
            elif isinstance(e, TypeError):
                return {schema_uri: [error_msg + "Invalid format."]}
            elif isinstance(e, RequestsConnectionError):
                return {schema_uri: [error_msg + "Connection Error."]}

    def validate_json(self, schema, json_object):
        """
        Validates a JSON object against a specified schema.

        Parameters:
        - schema (dict): The JSON schema to validate against.
        - json_object (dict): The JSON object to be validated.

        Returns:
        - list: A list of error messages, empty if valid.
        """
        errors = []
        validator = jsonschema.Draft7Validator(schema)
        for error in validator.iter_errors(json_object):
            path = "".join(f"[{v}]" for v in error.path)
            errors.append(f"{path}: {error.message}" if path else error.message)
        return errors

    def parse_and_validate(self, bco):
        """
        Parses and validates a BCO against both the base and extension schemas.

        Parameters:
        - bco (dict): The BioCompute Object to validate.

        Returns:
        - dict: A dictionary containing the validation results.
        """
        
        identifier = bco.get("object_id", "Unknown")
        results = {
            identifier: {
                'number_of_errors': 0, 
                'error_detail': [],
                'score': 0,
            }
        }

        # Validate against the base schema
        base_schema = self.load_schema(bco['spec_version'])
        base_errors = self.validate_json(base_schema, bco)
        results[identifier]['error_detail'].extend(base_errors)
        results[identifier]['number_of_errors'] += len(base_errors)

        if "usability_domain" in bco:
            results[identifier]['score'] = sum(len(s) for s in bco['usability_domain'])

        # Validate against extension schemas, if any
        for extension in bco.get("extension_domain", []):
            extension_schema_uri = extension.get("extension_schema")
            extension_schema = self.load_schema(extension_schema_uri)
            if not isinstance(extension_schema, dict):  # Validation passed
                extension_errors = self.validate_json(extension_schema, extension)
                results[identifier]['error_detail'].extend(extension_errors)
                results[identifier]['number_of_errors'] += len(extension_errors)

        return results

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
        """Update BCO

        Updates an existing BioCompute Object (BCO) draft instance with
        validated data.

        This method applies the validated changes to a BCO draft, including
        updating its contents and the list of authorized users. It also
        recalculates the `etag` of the BCO to reflect the new contents
        and ensures that the `last_update` timestamp is current. If a list of
        `authorized_users` is provided, this method replaces the current list
        of authorized users with the new list, allowing for dynamic access
        control to the BCO. Users not included in the new list will lose
        their access unless they are the owner or have other permissions.

        This method employs Django's atomic transactions to ensure database
        integrity during the update process. 

        Parameters:
        - instance (Bco):
            The BCO instance to be updated. This parameter is automatically
            supplied by the Django Rest Framework and not explicitly passed
            in the serializer's call.
        - validated_data (dict): 
            The data that has passed validation checks and is to be used to
            update the BCO instance. It includes updated `contents` and
            potentially a new list of `authorized_users`.

        Returns:
        - Bco: The updated BCO instance

        Raises:
        - Bco.DoesNotExist: 
            If the BCO instance with the specified `object_id` does not exist.
        - User.DoesNotExist:
            If one or more of the usernames in the `authorized_users` list do not correspond to valid User instances.
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
        bco_contents = bco_instance.contents
        bco_contents["provenance_domain"]["modified"] = datetime_converter(
            timezone.now()
        )
        etag = generate_etag(bco_contents)
        bco_instance.contents['etag'] = etag
        score = bco_score(bco_instance=bco_instance)
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
        score = bco_score(bco_instance=bco_instance)
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

    bco_contents_copy = copy.deepcopy(bco_contents)

    for key in ['object_id', 'spec_version', 'etag']:
            bco_contents_copy.pop(key, None)
    
    bco_etag = sha256(json.dumps(bco_contents).encode('utf-8')).hexdigest()
    return bco_etag

def check_etag_validity(bco_contents: dict) -> bool:
    """
    Check the validity of an ETag for a BioCompute Object (BCO).

    This function regenerates the ETag based on the current state of the BCO's contents,
    excluding the 'object_id', 'spec_version', and 'etag' fields, and compares it to the
    provided ETag. If both ETags match, it indicates that the BCO has not been altered in
    a way that affects its ETag, thus confirming its validity.

    Parameters:
    - bco_contents (dict):
        The current contents of the BCO.

    Returns:
    - bool:
        True if the provided ETag matches the regenerated one, False otherwise.
    """
    
    provided_etag = bco_contents.get("etag", "")
    bco_contents_copy = copy.deepcopy(bco_contents)

    for key in ['object_id', 'spec_version', 'etag']:
        bco_contents_copy.pop(key, None)

    regenerated_etag = sha256(json.dumps(bco_contents_copy).encode('utf-8')).hexdigest()

    return provided_etag == regenerated_etag

@transaction.atomic
def publish_draft(bco_instance: Bco, user: User, object: dict):
    """Create Published BCO
    """
    
    new_bco_instance = deepcopy(bco_instance)
    new_bco_instance.id = None
    new_bco_instance.state = "PUBLISHED"
    contents= new_bco_instance.contents
    if "published_object_id" in object:
        new_bco_instance.object_id = object["published_object_id"]
    else:
        version = contents['provenance_domain']['version']
        draft_deconstructed = object_id_deconstructor(object["object_id"])
        draft_deconstructed[-1] = version
        new_bco_instance.object_id = '/'.join(draft_deconstructed[1:])
    contents["object_id"] = new_bco_instance.object_id
    new_bco_instance.last_update = timezone.now()
    contents["provenance_domain"]["modified"] = datetime_converter(
        timezone.now()
    )
    contents["etag"] = generate_etag(contents)
    score = bco_score(bco_instance=new_bco_instance)

    new_bco_instance.save()

    if "delete_draft" in object and object["delete_draft"] is True:
        deleted = delete_draft(bco_instance=bco_instance, user=user)

    return new_bco_instance

def delete_draft(bco_instance:Bco, user:User,):
    """Delete Draft

    Delete draft bco
    """

    if bco_instance.owner == user:
        bco_instance.state = "DELETE"
        bco_instance.save()

    return "deleted"

def bco_score(bco_instance: Bco) -> Bco:
    """BCO Score 

    Process and score BioCompute Objects (BCOs).

    """

    contents = bco_instance.contents

    if "usability_domain" not in contents:
        bco_instance.score = 0
        return bco_instance
        
    try:
        usability_domain_length = sum(len(s) for s in contents['usability_domain'])
        score = {"usability_domain_length": usability_domain_length}
    except TypeError:
        score = {"usability_domain_length": 0}
        usability_domain_length = 0
    
    bco_instance.score = usability_domain_length
    
    return bco_instance
