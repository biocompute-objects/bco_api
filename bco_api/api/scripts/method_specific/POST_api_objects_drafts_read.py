# BCO model
from ...models import BCO

# For getting objects out of the database.
from ..utilities import DbUtils

# User information
from ..utilities import UserUtils

# Permisions for objects
from guardian.shortcuts import get_perms

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_api_objects_drafts_read(incoming):
    """
    Take the bulk request and read a draft object from it.
    """

    # Instantiate any necessary imports.
    db = DbUtils.DbUtils()
    uu = UserUtils.UserUtils()

    # The token has already been validated,
    # so the user is guaranteed to exist.

    # Get the User object.
    user = uu.user_from_request(
            rq=incoming
            )

    # Get the user's prefix permissions.
    px_perms = uu.prefix_perms_for_user(
            flatten=True,
            user_object=user,
            specific_permission=['view']
            )

    # Define the bulk request.
    bulk_request = incoming.data['POST_api_objects_drafts_read']

    # Construct an array to return the objects.
    returning = []
    any_failed = False

    # Since bulk_request is an array, go over each
    # item in the array.
    for read_object in bulk_request:
        # Get the prefix for this draft.
        standardized = read_object['object_id'].split('/')[-1].split('_')[0].upper()

        # Does the requestor have view permissions for
        # the *prefix*?
        if 'view_' + standardized in px_perms:

            # The requestor has view permissions for
            # the prefix, but do they have object-level
            # view permissions?

            # This can be checked by seeing if the requestor
            # is the object owner OR they are a user with
            # object-level view permissions OR if they are in a
            # group that has object-level view permissions.

            # To check these options, we need the actual object.
            if BCO.objects.filter(object_id=read_object['object_id']).exists():
                objected = BCO.objects.get(
                        object_id=read_object['object_id']
                        )

                # We don't care where the view permission comes from,
                # be it a User permission or a Group permission.
                all_permissions = get_perms(
                        user,
                        objected
                        )

                if user.username == objected.owner_user.username or 'view_' + standardized in all_permissions:

                    # Read the object.
                    returning.append(
                            db.messages(
                                    parameters={
                                            'contents' : objected.contents,
                                            'object_id': read_object['object_id']
                                            }
                                    )['200_OK_object_delete']
                            )

                else:

                    # Insufficient permissions.
                    returning.append(
                            db.messages(
                                    parameters={ }
                                    )['403_insufficient_permissions']
                            )
                    any_failed = True

            else:

                # Couldn't find the object.
                returning.append(
                        db.messages(
                                parameters={
                                        'object_id': read_object['object_id']
                                        }
                                )
                        ['404_object_id'])
                any_failed = True

        else:
            # Update the request status.
            returning.append(
                    db.messages(
                            parameters={
                                    'prefix': standardized
                                    }
                            )['401_prefix_unauthorized']
                    )
            any_failed = True

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    # For example, a table may not have been found for the first
    # requested draft.
    if any_failed:
        return Response(
                status=status.HTTP_300_MULTIPLE_CHOICES,
                data=returning
                )
    return Response(
            status=status.HTTP_200_OK,
            data=returning
            )
