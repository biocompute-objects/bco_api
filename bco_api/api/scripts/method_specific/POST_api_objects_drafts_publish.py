#!/usr/bin/env python3
"""Publish draft

publish a draft
"""

from api.models import bco

# For getting objects out of the database.
from api.scripts.utilities import DbUtils, UserUtils

# For the owner group
from django.contrib.auth.models import Group

# Permissions for objects
from guardian.shortcuts import get_perms

# Responses
from rest_framework import status
from rest_framework.response import Response


def POST_api_objects_drafts_publish(incoming):
    """Publish draft

    publish a draft
    
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
        request. A status of 300 means that some of the requests were
        successfull.
    """

    db_utils = DbUtils.DbUtils()

    # The token has already been validated,
    # so the user is guaranteed to exist.

    # Get the User object.
    user = UserUtils.UserUtils().user_from_request(request=incoming)

    # Get the user's prefix permissions.
    px_perms = UserUtils.UserUtils().prefix_perms_for_user(flatten=True, user_object=user)

    # Define the bulk request.
    bulk_request = incoming.data['POST_api_objects_drafts_publish']

    # Construct an array to return the objects.
    returning = []
    any_failed = False
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
            # the prefix, but do they have object-level
            # publish permissions?

            # This can be checked by seeing if the requestor
            # is the object owner OR they are a user with
            # object-level publish permissions OR if they are in a
            # group that has object-level publish permissions.

            # To check these options, we need the actual object
            # AND the requestor must have publish permissions
            # on the draft.
            if bco.objects.filter(object_id=publish_object['draft_id'], state='DRAFT').exists():
                objected = bco.objects.get(object_id=publish_object['draft_id'])

                # We don't care where the publish permission comes from,
                # be it a User permission or a Group permission.
                all_permissions = get_perms(user, objected)

                # TODO: replace with guardian has_perm?
                if user.username == objected.owner_user.username or 'publish_' + publish_object['draft_id'] in all_permissions:

                    # The draft ID exists and the requestor has the right permissions.

                    # If an object_id is given with the request,
                    # it means that we are trying to publish
                    # a new version of an existing published object (on this server).

                    # Attempt to publish, but first, verify
                    # that the object is IEEE-compliant.
                    # schema_check = ju.check_object_against_schema(
                    # 	object_pass = objected,
                    # 	schema_pass =
                    # )
                    # TODO: fix the schema check...
                    schema_check = None

                    if schema_check is None:
                        # Go straight to the publish attempt if there is no
                        # object_id key given with the request.
                        if 'object_id' not in publish_object:

                            # Object is compliant, so kick it off to
                            # be published.

                            # For publishing, the owner group and the
                            # owner user are "the same".  That is, the
                            # owner group is the one derived from the owner user.
                            published = db_utils.publish(
                                    og=Group.objects.get(name=user.username).name,
                                    ou=user.username,
                                    prfx=standardized,
                                    publishable=objected.contents,
                                    publishable_id='new'
                                    )

                            # Did the publishing go well?
                            if type(published) is dict:
                                # Lastly, if we were given the directive to delete
                                # the draft on publish, process that.

                                # Does the requestor have delete permissions on
                                # the object?
                                if 'delete_draft' in publish_object:
                                    if publish_object['delete_draft']:
                                        if 'delete_' + publish_object['draft_id'] in all_permissions:
                                            objected.delete()
                                            # Draft was published and deleted as requested.
                                            returning.append(db_utils.messages(parameters={
                                                    'published_id': published['published_id'] })['200_OK_object_publish_draft_deleted'])
                                        else:
                                            # Draft failed to delete because of permissions, but object was published
                                            returning.append(db_utils.messages(parameters={
                                                    'published_id': published['published_id'] })['200_OK_object_publish_draft_failed_delete'])
                                    else:
                                        # Draft was published, but not deleted since not requested
                                        returning.append(db_utils.messages(parameters={
                                                'published_id': published['published_id'] })['200_OK_object_publish'])
                                else:
                                    # Draft was published, but not deleted since not requested (not included in request)
                                    returning.append(db_utils.messages(parameters={
                                            'published_id': published['published_id'] })['200_OK_object_publish'])

                        else:
                            # Published object owner automatically has publish
                            # permissions, but we need to check for the publish
                            # permission otherwise.
                            if user.username == objected.owner_user.username or 'publish_new_version_' + publish_object['object_id'] in all_permissions:

                                # We need to check that the provided object ID
                                # complies with the versioning rules.
                                versioned = db_utils.check_version_rules(published_id=publish_object['object_id'])

                                # If we get a dictionary back, that means we have
                                # a usable object ID.  Otherwise, something went wrong
                                # with trying to use the provided object ID.
                                if type(versioned) is dict:
                                    # We now have the published_id to write with.
                                    published = db_utils.publish(
                                            owner_group=Group.objects.get(name=user.username).name,
                                            owner_user=user.username,
                                            prefix=standardized,
                                            publishable=objected,
                                            publishable_id=versioned
                                            )

                                    # Did the publishing go well?
                                    if type(published) is dict:
                                        import pdb; pdb.set_trace()
                                        # Update the request status.
                                        returning.append(db_utils.messages(parameters=versioned)['200_OK_object_publish'])

                                        # Lastly, if we were given the directive to delete
                                        # the draft on publish, process that.

                                        # Does the requestor have delete permissions on
                                        # the object?
                                        if 'delete_draft' in publish_object:
                                            if publish_object['delete_draft'] and 'delete_' + publish_object['draft_id'] in all_permissions:
                                                objected.delete()

                                else:
                                    # Either the object wasn't found
                                    # or an invalid version number was provided.
                                    if versioned == 'bad_version_number':
                                        returning.append(db_utils.messages(parameters={ })['400_bad_version_number'])
                                    elif versioned == 'non_root_id':
                                        returning.append(db_utils.messages(parameters={ })['400_non_root_id'])
                                    else:
                                        # Unspecified error, here as a trap.
                                        returning.append(db_utils.messages(parameters={ })['400_unspecified_error'])
                                    any_failed = True

                            else:
                                # Insufficient permissions.
                                returning.append(db_utils.messages(parameters={ })['403_insufficient_permissions'])
                                any_failed = True

                    else:
                        # Object provided is not schema-compliant.
                        returning.append(db_utils.messages(parameters={
                                'errors': schema_check })['400_non_publishable_object'])
                        any_failed = True

                else:
                    # Insufficient permissions.
                    returning.append(db_utils.messages(parameters={ })['403_insufficient_permissions'])
                    any_failed = True

            else:
                # print(publish_object)
                # Couldn't find the object.
                returning.append(db_utils.messages(parameters={
                        'object_id': publish_object['draft_id'] })['404_object_id'])
                any_failed = True

        else:
            # Update the request status.
            returning.append(db_utils.messages(parameters={
                    'prefix': standardized })['401_prefix_unauthorized'])
            any_failed = True

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    # For example, a table may not have been found for the first
    # requested draft.
    if any_failed:
        # import pdb; pdb.set_trace()
        return Response(status=status.HTTP_300_MULTIPLE_CHOICES, data=returning)

    return Response(status=status.HTTP_200_OK, data=returning)
