#!/usr/bin/env python3

"""Create BCO Draft

--------------------
Creates a new BCO draft object.
"""
from api.models import BCO
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
    root_uri = settings.OBJECT_NAMING['root_uri']
    # Construct an array to return the objects.
    returning = []
    any_failed = False

    # Since bulk_request is an array, go over each
    # item in the array.

    for creation_object in bulk_request:
        prefix = creation_object["prefix"].upper()
        # Require the macro-level and draft-specific permissions.
        if (
            "add_" + prefix in prefix_perms
            and "draft_" + prefix in prefix_perms
        ):
            prefix_counter = prefix_table.objects.get(prefix=prefix)
            if "object_id" in creation_object:
                if BCO.objects.filter(object_id=creation_object['object_id']).exists():
                    returning.append(
                        db_utils.messages(parameters={"object_id": creation_object['object_id']})[
                            "409_object_conflict"
                        ]
                    )
                    any_failed = True
                    continue
                constructed_obj_id = creation_object['object_id']
            else:
                object_num = format(prefix_counter.n_objects, "06d")
                constructed_obj_id = (root_uri+'/'+prefix+'_'+object_num+'/DRAFT')
                creation_object["object_id"] = constructed_obj_id

            if Group.objects.filter(
                name=creation_object["owner_group"].lower()
            ).exists():

                # TODO: abstract this out to DbUtils.
                # constructed_name = object_naming_info["uri_regex"].replace(
                #     "root_uri", object_naming_info["root_uri"]
                # )
                # constructed_name = constructed_name.replace("prefix", prefix)

                # prefix_location = constructed_name.index(prefix)
                # prefix_length = len(prefix)
                # constructed_name = constructed_name[0 : prefix_location + prefix_length]
                # 
                # creation_object["object_id"] = (
                #     constructed_name
                #     + "_"
                #     + "{:06d}".format(prefix_counter.n_objects)
                #     + "/DRAFT"
                # )
                # Make sure to create the object ID field in our draft.
                creation_object["contents"]["object_id"] = constructed_obj_id
                # Instantiate the owner group as we'll need it a few times here.
                owner_group = Group.objects.get(name=creation_object["owner_group"])

                # Django wants a primary key for the Group...
                creation_object["owner_group"] = owner_group.name

                # Set the owner user (the requestor).
                creation_object["owner_user"] = user.username

                # Give the creation object the prefix.
                creation_object["prefix"] = prefix

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

                if objects_written < 1:
                    # Issue with writing out to DB
                    returning.append(
                        db_utils.messages(parameters={})["400_bad_request"]
                    )
                    any_failed = True
                prefix_counter.n_objects = prefix_counter.n_objects + 1
                prefix_counter.save()
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
