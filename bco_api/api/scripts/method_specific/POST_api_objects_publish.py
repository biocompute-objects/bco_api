#!/usr/bin/env python3
"""publish

--------------------
Take the bulk request and publish objects directly.
"""

from ...models import bco
# For getting objects out of the database.
from ..utilities import DbUtils

# User information
from ..utilities import UserUtils

# For the owner group
from django.contrib.auth.models import Group

# Permissions for objects
from guardian.shortcuts import get_perms

# Responses
from rest_framework import status
from rest_framework.response import Response

def POST_api_objects_publish(request):
    """
    Take the bulk request and publish objects directly.
    """

    # Instantiate any necessary imports.
    db = DbUtils.DbUtils()
    uu = UserUtils.UserUtils()

    # The token has already been validated,
    # so the user is guaranteed to exist.

    # Get the User object.
    user = uu.user_from_request(
        request = request
    )

    # Get the user's prefix permissions.
    px_perms = uu.prefix_perms_for_user(
        flatten = True,
        user_object = user
    )

    # Define the bulk request.
    bulk_request = request.data['POST_api_objects_publish']

    # Construct an array to return the objects.
    returning = []

    # Since bulk_request is an array, go over each
    # item in the array.
    for publish_object in bulk_request:

        # Attempting to publish from a draft ID.

        # Get the prefix *that we are publishing under*
        # (this prefix is not necessarily the same one
        # as the draft was created under).
        standardized = publish_object['prefix']

        # Does the requestor have publish permissions for
        # the *prefix*?
        if 'publish_' + standardized in px_perms:
        
            # The requestor has publish permissions for
            # the prefix.  If no object ID is provided,
            # proceed straight to the publish attempt.
                
            # Attempt to publish, but first, verify
            # that the object is IEEE-compliant.
            # schema_check = ju.check_object_against_schema(
            #     object_pass = objected,
            #     schema_pass = 
            # )
            # TODO: fix the schema check...
            schema_check = None

            if schema_check is None:

                # If an object_id is given with the request,
                # it means that we are trying to publish
                # a new version of an existing published object (on this server).

                # Go straight to the publish attempt if there is no
                # object_id key given with the request.
                if 'object_id' not in publish_object:

                    # Object is compliant, so kick it off to
                    # be published.

                    # For publishing, the owner group and the
                    # owner user are "the same".  That is, the
                    # owner group is the one derived from the owner user.
                    published = db.publish(
                        og = Group.objects.get(name = user.username).name,
                        ou = user.username,
                        prfx = standardized,
                        publishable = publish_object["contents"],
                        publishable_id = 'new'
                    )


                    # Did the publishing go well?
                    if isinstance(published, dict):

                        # Update the request status.
                        returning.append(
                            db.messages(
                                parameters = {
                                    'published_id': published['published_id']
                                }
                            )['200_OK_object_publish']
                        )

                else:

                    # When an object ID is provided, the requestor must
                    # have publish permissions for the published object.
                    objected = bco.objects.get(
                        object_id = publish_object['object_id']
                    )

                    # We don't care where the publish permission comes from,
                    # be it a User permission or a Group permission.
                    all_permissions = get_perms(user,objected)
                    # Published object owner automatically has publish
                    # permissions, but we need to check for the publish
                    # permission otherwise.
                    if user.username == objected.owner_user.username or 'publish_new_version_' + publish_object['object_id'] in all_permissions:

                        # We need to check that the provided object ID
                        # complies with the versioning rules.
                        versioned = db.check_version_rules(
                            published_id = publish_object['object_id']
                        )

                        # If we get a dictionary back, that means we have
                        # a usable object ID.  Otherwise, something went wrong
                        # with trying to use the provided object ID.
                        if isinstance(versioned, dict):

                            # We now have the published_id to write with.

                            # For publishing, the owner group and the
                            # owner user are "the same".  That is, the
                            # owner group is the one derived from the owner user.
                            published = db.publish(
                                og = Group.objects.get(name = user.username).name,
                                ou = user.username,
                                prfx = standardized,
                                publishable = publish_object['contents'],
                                publishable_id = versioned
                            )

                            # Did the publishing go well?
                            if isinstance(published, dict):

                                # Update the request status.
                                returning.append(
                                    db.messages(
                                        parameters = {
                                            'published_id': versioned
                                        }
                                    )['200_OK_object_publish']
                                )
                        else:
                            # Either the object wasn't found
                            # or an invalid version number was provided.
                            if versioned == 'bad_version_number':
                                returning.append(
                                    db.messages(
                                        parameters = {}
                                    )['400_bad_version_number']
                                )
                            elif versioned == 'non_root_id':
                                returning.append(
                                    db.messages(
                                        parameters = {}
                                    )['400_non_root_id']
                                )
                    
                    else:

                        # Insufficient permissions.
                        returning.append(db.messages(parameters = {}
                            )['403_insufficient_permissions']
                        )

            else:
                # Object provided is not schema-compliant.
                returning.append(db.messages(
                    parameters = {'errors': schema_check}
                    )['400_non_publishable_object']
                )
        else:
            # Update the request status.
            returning.append(db.messages(
                parameters = {'prefix': standardized}
                )['401_prefix_unauthorized']
            )

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    # For example, a table may not have been found for the first
    # requested draft.
    return Response(status = status.HTTP_200_OK,data = returning)
