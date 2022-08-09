#!/usr/bin/env python3
"""Modify Draft Object

--------------------
Modifies a BCO object.  The BCO object must be a draft in order to be
modifiable.  The contents of the BCO will be replaced with the new
contents provided in the request body.
"""

from api.models import BCO
from api.scripts.utilities import DbUtils
from api.scripts.utilities import UserUtils

from django.utils import timezone
from guardian.shortcuts import get_perms
from rest_framework import status
from rest_framework.response import Response

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/


def post_api_objects_drafts_modify(request):
    """Modify Draft

    Take the bulk request and modify a draft object from it.

    Parameters
    ----------
    request: rest_framework.request.Request
            Django request object.

    Returns
    -------
    rest_framework.response.Response
        An HttpResponse that allows its data to be rendered into arbitrary
        media types. As this view is for a bulk operation, status 200 means
        that the request was successfully processed for each item in the
        request. A status of 207 means that some of the requests were
        successfull.
    """

    db_utils = DbUtils.DbUtils()
    user = UserUtils.UserUtils().user_from_request(request=request)
    bulk_request = request.data["POST_api_objects_drafts_modify"]
    px_perms = UserUtils.UserUtils().prefix_perms_for_user(
        flatten=True, user_object=user, specific_permission=["add"]
    )

    # Construct an array to return the objects.
    returning = []
    any_failed = False
    for draft_object in bulk_request:
        # Get the prefix for this draft.
        prefix = draft_object["object_id"].split("/")[-2].split("_")[0].upper()

        # Does the requestor have change permissions for
        # the *prefix*?

        # TODO: add permission setting view...
        # if 'change_' + prefix in px_perms:
        if "add_" + prefix in px_perms:

            # The requestor has change permissions for
            # the prefix, but do they have object-level
            # change permissions?

            # This can be checked by seeing if the requestor
            # is the object owner OR they are a user with
            # object-level change permissions OR if they are in a
            # group that has object-level change permissions.
            # To check these options, we need the actual object.

            if draft_object["object_id"] != draft_object["contents"]["object_id"]:
                returning.append(
                    db_utils.messages(
                        parameters={
                            "object_id": draft_object["contents"]["object_id"],
                            "draft_object_id": draft_object["object_id"],
                        }
                    )["409_draft_object_id_conflict"]
                )
                any_failed = True
                continue

            if BCO.objects.filter(
                object_id=draft_object["contents"]["object_id"]
            ).exists():
                objected = BCO.objects.get(
                    object_id=draft_object["contents"]["object_id"]
                )

                # We don't care where the view permission comes from,
                # be it a User permission or a Group permission.
                all_permissions = get_perms(user, objected)
                # TODO: add permission setting view...
                if (
                    user.username == objected.owner_user.username
                    or "add_" + prefix in px_perms
                ):

                    # # User does *NOT* have to be in the owner group!
                    # # to assign the object's group owner.
                    # if Group.objects.filter(
                    #     name = draft_object['owner_group'].lower()
                    # ).exists():
                    #
                    # Update the object.
                    # *** COMPLETELY OVERWRITES CONTENTS!!! ***
                    objected.contents = draft_object["contents"]

                    if "state" in draft_object:
                        if draft_object["state"] == "DELETE":
                            objected.state = "DELETE"

                    # Set the update time.
                    objected.last_update = timezone.now()

                    # Save it.
                    objected.save()

                    # Update the request status.
                    returning.append(
                        db_utils.messages(
                            parameters={"object_id": draft_object["object_id"]}
                        )["200_update"]
                    )
                else:
                    # Insufficient permissions.
                    returning.append(
                        db_utils.messages(parameters={})["403_insufficient_permissions"]
                    )
                    any_failed = True

            else:
                returning.append(
                    db_utils.messages(
                        parameters={"object_id": draft_object["object_id"]}
                    )["404_object_id"]
                )
                any_failed = True
        else:
            returning.append(
                db_utils.messages(parameters={"prefix": prefix})[
                    "401_prefix_unauthorized"
                ]
            )
            any_failed = True
    if any_failed and len(returning) == 1:
        if returning[0]["status_code"] == "403":
            return Response(status=status.HTTP_403_FORBIDDEN, data=returning)
        else:
            return Response(status=status.HTTP_207_MULTI_STATUS, data=returning)
    if any_failed and len(returning) > 1:
        return Response(status=status.HTTP_207_MULTI_STATUS, data=returning)
    else:
        return Response(status=status.HTTP_200_OK, data=returning)
