#!/usr/bin/env python3

"""Create BCO Draft

--------------------
Creates a new BCO draft object.
"""
import json
from email import message
from api.scripts.utilities import DbUtils, UserUtils
from api.model.prefix import prefix_table
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response


def post_api_objects_drafts_create(request):
    """Create BCO Draft

    Parameters
    ----------
    request: rest_framework.request.
        Django request object.

    Returns
    -------
    rest_framework.response.Response
        An HttpResponse that allows its data to be rendered into
        arbitrary media types.
    """

    db_utils = DbUtils.DbUtils()
    user = UserUtils.UserUtils().user_from_request(request=request)
    prefix_perms = UserUtils.UserUtils().prefix_perms_for_user(
        flatten=True, user_object=user, specific_permission=["add"]
    )

    # Define the bulk request.
    bulk_request = request.data["POST_api_objects_draft_create"]

    # Get the object naming information.
    object_naming_info = settings.OBJECT_NAMING

    # Construct an array to return the objects.
    returning = []
    any_failed = False

    # Since bulk_request is an array, go over each
    # item in the array.

    # TODO: Not sure why the first one is treated differently if there is a single
    #       request.  Need to compare the code - the second block might be all we
    #       need.
    if len(bulk_request) == 1:
        creation_object = bulk_request[0]
        standardized = creation_object["prefix"].upper()
        if (
            "add_" + standardized in prefix_perms
            and "draft_" + standardized in prefix_perms
        ):
            if Group.objects.filter(
                name=creation_object["owner_group"].lower()
            ).exists():
                constructed_name = object_naming_info["uri_regex"].replace(
                    "root_uri", object_naming_info["root_uri"]
                )
                constructed_name = constructed_name.replace("prefix", standardized)
                prefix_location = constructed_name.index(standardized)
                prefix_length = len(standardized)
                constructed_name = constructed_name[0 : prefix_location + prefix_length]
                prefix_counter = prefix_table.objects.get(prefix=standardized)
                creation_object["object_id"] = (
                    constructed_name
                    + "_"
                    + "{:06d}".format(prefix_counter.n_objects)
                    + "/DRAFT"
                )
                # import pdb; pdb.set_trace()
                creation_object["contents"]["object_id"] = creation_object["object_id"]
                bco_id = creation_object["object_id"]
                owner_group = Group.objects.get(name=creation_object["owner_group"])
                creation_object["owner_group"] = owner_group.name
                creation_object["owner_user"] = user.username
                creation_object["prefix"] = standardized
                creation_object["state"] = "DRAFT"
                creation_object["last_update"] = timezone.now()
                objects_written = db_utils.write_object(
                    p_app_label="api",
                    p_model_name="BCO",
                    p_fields=[
                        "contents",
                        "last_update",
                        "object_id",
                        "owner_group",
                        "owner_user",
                        "prefix",
                        "schema",
                        "state",
                    ],
                    p_data=creation_object,
                )
                prefix_counter.n_objects = prefix_counter.n_objects + 1
                prefix_counter.save()

                if objects_written < 1:
                    # Issue with writing out to DB
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data="The request could not be processed with the"
                        " parameters provided.",
                    )

                return Response(
                    status=status.HTTP_201_CREATED,
                    data={
                        "request_status": "SUCCESS",
                        "status_code": "201",
                        "message": f"The object with ID {bco_id} was"
                        " created on the server.",
                        "object_id": bco_id,
                    },
                )

            else:
                # Update the request status.
                returning.append(db_utils.messages(parameters={})["400_bad_request"])
                any_failed = True

        else:
            # Update the request status.
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={
                    "request_status": "FAILURE",
                    "status_code": "401",
                    "message": "The token provided does not have draft"
                    f"permissions for prefix {standardized}.",
                },
            )

    for creation_object in bulk_request:
        # Standardize the prefix.
        import pdb

        pdb.set_trace()
        standardized = creation_object["prefix"].upper()

        # Require the macro-level and draft-specific permissions.
        if (
            "add_" + standardized in prefix_perms
            and "draft_" + standardized in prefix_perms
        ):

            # Make sure the group the object is being
            # assigned to exists.

            # User does *NOT* have to be in the owner group!
            # to assign the object's group owner.
            if Group.objects.filter(
                name=creation_object["owner_group"].lower()
            ).exists():

                # TODO: abstract this out to DbUtils.

                # The prefix permission exists and the presumptive
                # group owner also exists, so write the object.

                # Source: https://www.webforefront.com/django/singlemodelrecords.html

                # Create the ID template.

                # Use the root URI and prefix to construct the name.
                constructed_name = object_naming_info["uri_regex"].replace(
                    "root_uri", object_naming_info["root_uri"]
                )
                constructed_name = constructed_name.replace("prefix", standardized)

                # Get rid of the rest of the regex for the name.
                prefix_location = constructed_name.index(standardized)
                prefix_length = len(standardized)
                constructed_name = constructed_name[0 : prefix_location + prefix_length]
                # Create a draft ID that is essentially randomized.
                prefix_counter = prefix_table.objects.get(prefix=standardized)
                creation_object["object_id"] = (
                    constructed_name
                    + "_"
                    + "{:06d}".format(prefix_counter.n_objects)
                    + "/DRAFT"
                )

                # Make sure to create the object ID field in our draft.
                creation_object["contents"]["object_id"] = creation_object["object_id"]

                # Instantiate the owner group as we'll need it a few times here.
                owner_group = Group.objects.get(name=creation_object["owner_group"])

                # Django wants a primary key for the Group...
                creation_object["owner_group"] = owner_group.name

                # Set the owner user (the requestor).
                creation_object["owner_user"] = user.username

                # Give the creation object the prefix.
                creation_object["prefix"] = standardized

                # This is a DRAFT.
                creation_object["state"] = "DRAFT"

                # Set the datetime properly.
                creation_object["last_update"] = timezone.now()

                # Write to the database.
                objects_written = db_utils.write_object(
                    p_app_label="api",
                    p_model_name="bco",
                    p_fields=[
                        "contents",
                        "last_update",
                        "object_id",
                        "owner_group",
                        "owner_user",
                        "prefix",
                        "schema",
                        "state",
                    ],
                    p_data=creation_object,
                )
                prefix_counter.n_objects = prefix_counter.n_objects + 1
                prefix_counter.save()

                if objects_written < 1:
                    # Issue with writing out to DB
                    returning.append(
                        db_utils.messages(parameters={})["400_bad_request"]
                    )
                    any_failed = True

                # Object creator automatically has full permissions
                # on the object.  This is checked by checking whether
                # or not the requestor matches the owner_user primary
                # key OR if they are in a group with given permissions
                # (not done here, but in the urls that request
                # a draft object, i.e. (GET) <str:draft_object_id>
                # and (POST) api/objects/read/).

                # The owner group is given permissions in the post_save
                # receiver in models.py

                # Update the request status.
                returning.append(
                    db_utils.messages(parameters=creation_object)["201_create"]
                )

            else:
                # Update the request status.
                returning.append(db_utils.messages(parameters={})["400_bad_request"])
                any_failed = True

        else:
            # Update the request status.
            returning.append(
                db_utils.messages(parameters={"prefix": creation_object["prefix"]})[
                    "401_prefix_unauthorized"
                ]
            )
            any_failed = True

    if any_failed:
        return Response(status=status.HTTP_207_MULTI_STATUS, data=returning)

    return Response(status=status.HTTP_200_OK, data=returning)
