#!/usr/bin/env python3
"""Publish draft

publish a draft
"""

from api.models import bco, prefix_table
from api.scripts.utilities import DbUtils, UserUtils
from django.contrib.auth.models import Group
from django.utils import timezone
from guardian.shortcuts import get_perms
from rest_framework import status
from rest_framework.response import Response


def POST_api_objects_drafts_publish(request):
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

    returning = []
    any_failed = False
    db_utils = DbUtils.DbUtils()
    user = UserUtils.UserUtils().user_from_request(request=request)
    prefix_perms = UserUtils.UserUtils().prefix_perms_for_user(
        flatten=True, user_object=user
    )
    bulk_request = request.data['POST_api_objects_drafts_publish']
    for publish_object in bulk_request:
        prefix = publish_object['prefix']
        prefix_counter = prefix_table.objects.get(prefix=prefix)
        delete_draft = publish_object['delete_draft']
        draft_id = publish_object['draft_id']
        if 'object_id' not in publish_object:
            object_id = publish_object['draft_id'].split('/')[0:4]
            object_id.append('1.0')
            object_id = '/'.join(object_id)
        else:
            object_id = publish_object['object_id']

        versioned = {'published_id': object_id}
        # versioned = db_utils.check_version_rules(
        #     published_id=object_id
        # )
        prefix_auth = 'publish_' + prefix in prefix_perms
        draft_exists = (bco.objects.filter(object_id=publish_object['draft_id'],
                state='DRAFT').exists()
        )

        if draft_exists is True:
            objected = bco.objects.get(object_id=publish_object['draft_id'])
            all_permissions = get_perms(user, objected)
            is_owner = user.username == objected.owner_user.username
            owner_group = Group.objects.get(name=user.username)
            can_publish = 'publish_' + publish_object['draft_id'] in all_permissions
            if prefix_auth is True:
                if is_owner is True or can_publish is True:
                    if delete_draft is True:
                        print('overwirting draft')
                        objected.last_update = timezone.now()
                        objected.state = 'PUBLISHED'
                        objected.owner_group = owner_group
                        objected.object_id = versioned['published_id']
                        objected.contents['object_id'] = versioned['published_id']
                        objected.save()

                        # Update the request status.
                        returning.append(db_utils.messages(
                            parameters=versioned)['200_OK_object_publish_draft_deleted']
                        )

                    else:
                        new_object = {}
                        print('making a new one!')
                        new_object['contents'] = objected.contents
                        new_object['object_id'] = object_id
                        new_object['contents']['object_id'] = object_id
                        new_object['owner_group'] = owner_group
                        new_object['owner_user'] = objected.owner_user
                        new_object['prefix'] = objected.prefix
                        new_object['last_update'] = timezone.now()
                        new_object['schema'] = 'IEEE'
                        new_object['state'] = 'PUBLISHED'

                        # Write to the database.
                        objects_written = db_utils.write_object(
                            p_app_label = 'api',
                            p_model_name = 'bco',
                            p_fields = [
                                'contents',
                                'last_update',
                                'object_id',
                                'owner_group',
                                'owner_user',
                                'prefix',
                                'schema',
                                'state'],
                            p_data = new_object
                        )
                        prefix_counter.n_objects = prefix_counter.n_objects + 1
                        prefix_counter.save()
                        if objects_written < 1:
                            # Issue with writing out to DB
                            returning.append(db_utils.messages(parameters={ })['400_bad_request'])
                            any_failed = True
                        else:
                            # Update the request status.
                            returning.append(db_utils.messages(
                                parameters=versioned)['200_OK_object_publish_draft_failed_delete']
                            )

                else:
                    # Insufficient permissions.
                    returning.append(db_utils.messages(
                        parameters={ })['403_insufficient_permissions']
                    )
                    any_failed = True

            else:
            # Update the request status.
                returning.append(db_utils.messages(
                    parameters={'prefix': prefix })['401_prefix_unauthorized'])
                any_failed = True

        else:
         # Couldn't find the object.
            returning.append(db_utils.messages(
                parameters={'object_id': publish_object['draft_id'] }
                )['404_object_id']
            )
            any_failed = True

        #                 published = db_utils.publish(
        #                     owner_group=Group.objects.get(
        #                         name=user.username
        #                     ).name,
        #                     owner_user = user.username,
        #                     prefix = prefix,
        #                     publishable = objected,
        #                     publishable_id = object_id,
        #                     replace_draft = delete_draft
        #                 )

        #                 # Did the publishing go well?
        #                 if type(published) is dict:
        #                     # Update the request status.
        #                     returning.append(db_utils.messages(
        #                         parameters=versioned)['200_OK_object_publish']
        #                     )

        #                     # Lastly, if we were given the directive to delete
        #                     # the draft on publish, process that.

        #                     # Does the requestor have delete permissions on
        #                     # the object?


    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    # For example, a table may not have been found for the first
    # requested draft.
    if any_failed:
        return Response(status=status.HTTP_300_MULTIPLE_CHOICES, data=returning)

    return Response(status=status.HTTP_200_OK, data=returning)
# Attempt to publish, but first, verify
# that the object is IEEE-compliant.
# TODO: fix the schema check...
# schema_check = ju.check_object_against_schema(
# 	object_pass = objected,
# 	schema_pass =
# )


    # published = db_utils.publish(
    #     owner_group=Group.objects.get(name=user.username).name,
    #     owner_useru=user.username,
    #     prefix=prefix,
    #     publishable=objected.contents,
    #     publishable_id='new'
    # )

    # # Did the publishing go well?
    # if type(published) is dict:
    #     # Lastly, if we were given the directive to delete
    #     # the draft on publish, process that.

    #     # Does the requestor have delete permissions on
    #     # the object?
    #     if 'delete_draft' in publish_object:
    #         if publish_object['delete_draft']:
    #             if 'delete_' + publish_object['draft_id'] in all_permissions:
    #                 objected.delete()
    #                 # Draft was published and deleted as requested.
    #                 returning.append(db_utils.messages(parameters={
    #                         'published_id': published['published_id'] })['200_OK_object_publish_draft_deleted'])
    #             else:
    #                 # Draft failed to delete because of permissions, but object was published
    #                 returning.append(db_utils.messages(parameters={
    #                         'published_id': published['published_id'] })['200_OK_object_publish_draft_failed_delete'])
    #         else:
    #             # Draft was published, but not deleted since not requested
    #             returning.append(db_utils.messages(parameters={
    #                     'published_id': published['published_id'] })['200_OK_object_publish'])
    #     else:
    #         # Draft was published, but not deleted since not requested (not included in request)
    #         returning.append(db_utils.messages(parameters={
    #                 'published_id': published['published_id'] })['200_OK_object_publish'])
