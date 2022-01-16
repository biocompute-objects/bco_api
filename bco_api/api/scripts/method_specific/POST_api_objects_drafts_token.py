# BCOs
import semver

from ...models import bco

# User information
from ..utilities import UserUtils

# Object-level permissions
from guardian.shortcuts import get_objects_for_user

# Concatenating QuerySets
from itertools import chain

# Responses
from rest_framework import status
from rest_framework.response import Response

# Below is helper code to deal with how we are allowing non standard versions (i.e. 1.2 instead of 1.2.0, etc).
import re
from semver import VersionInfo as Version
from typing import Optional, Tuple

BASEVERSION = re.compile(
        r"""[vV]?
        (?P<major>0|[1-9]\d*)
        (\.
        (?P<minor>0|[1-9]\d*)
        (\.
            (?P<patch>0|[1-9]\d*)
        )?
        )?
    """,
        re.VERBOSE,
        )


def coerce(version: str) -> Tuple[Version, Optional[str]]:
    """
    Convert an incomplete version string into a semver-compatible Version
    object

    * Tries to detect a "basic" version string (``major.minor.patch``).
    * If not enough components can be found, missing components are
        set to zero to obtain a valid semver version.

    :param str version: the version string to convert
    :return: a tuple with a :class:`Version` instance (or ``None``
        if it's not a version) and the rest of the string which doesn't
        belong to a basic version.
    :rtype: tuple(:class:`Version` | None, str)
    """
    match = BASEVERSION.search(version)
    if not match:
        return (None, version)

    ver = {
            key: 0 if value is None else value for key, value in match.groupdict().items()
            }
    ver = Version(**ver)
    rest = match.string[match.end():]  # noqa:E203
    return ver, rest


def POST_api_objects_drafts_token(
        rqst,
        internal=False
        ):
    """
    Get all DRAFT objects for a token.

    rqst - the request object
    internal - is the call being made to this handler
    internally?
    """
    print("In the POST_api_objects_drafts_token call")
    # import pdb;pdb.set_trace()
    # The token has already been validated,
    # so the user is guaranteed to exist.

    # Get the user's info.
    # Instantiate UserUtils.
    uu = UserUtils.UserUtils()

    # Get the user object.
    ui = uu.user_from_request(rq=rqst)

    # Any object that a user has access to
    # in any way counts as an "object".
    # That is, any permission counts as
    # a "view" permission...

    # However, the prefix permissions must
    # be in place for the user to view
    # anything.  Recall that prefix
    # permissions override any object-level
    # permissions.

    # We can't just use a straight filter here
    # because we have to use two different
    # models (the prefix permissions on the
    # one hand and the BCO objects on the other).

    # First, get all prefixes available to the
    # user.
    user_prefixes = uu.prefixes_for_user(user_object=ui)

    # Now get any object where the user has an
    # object-level permission.

    # Use an empty list of perms to get ANY perm.
    # Source: https://stackoverflow.com/a/24980558
    user_objects = get_objects_for_user(
            user=ui,
            perms=[],
            klass=bco,
            any_perm=True
            )

    # Now get all objects under these prefixes.
    prefix_objects = bco.objects.filter(
            prefix__in=user_prefixes,
            state='DRAFT'
            )

    # Assume all the values are supposed to be returned.
    # Source: https://stackoverflow.com/a/51733590
    return_values = ['contents', 'last_update', 'object_class', 'object_id', 'owner_group', 'owner_user', 'prefix',
                     'schema', 'state']

    # If there are any valid keys in the request,
    # use them to narrow down the fields.

    # Redundant logic here since the schema check
    # would catch this...
    if 'fields' in rqst.data['POST_api_objects_drafts_token']:

        # Take the fields and find their intersection with
        # the available fields.
        # Source: https://stackoverflow.com/a/3697438
        common_fields = list(
                set(rqst.data['POST_api_objects_drafts_token']['fields']) &
                set(return_values)
                )

        if len(common_fields) > 0:
            return_values = common_fields

    # Return based on whether or not we're using an internal
    # call.
    if not internal:
        print(" Not Internal, user response: {}".format(user_objects.intersection(prefix_objects).values(*return_values)))
        # Get the user's DRAFT objects.
        return Response(
                data=user_objects.intersection(prefix_objects).values(*return_values),
                status=status.HTTP_200_OK
                )

    elif internal:

        # Concatenate the QuerySets.
        # Source: https://stackoverflow.com/a/434755

        # Get the user's DRAFT objects AND
        # add in the published objects.
        # TODO: This needs to only return the most recent PUBLISHED objects not all of the versions
        # import pdb; pdb.set_trace()

        published = bco.objects.filter(state='PUBLISHED').values()
        # unique_published = []
        unique_published = set()

        # E.g.
        # published[0]["contents"]["object_id"] = 'http://127.0.0.1:8000/BCO_000010/1.0'

        bcos = { }
        for p in published:
            # TODO: We should move this out of a try except and try to handle various situations, this is currently
            #       assuming that the format is http://URL:PORT/BCO NAME/BCO VERSION - this may not always be true
            try:
                bco_url, bco_id_name, bco_id_version = p["contents"]["object_id"].rsplit("/", 2)
            except Exception as e:
                print("Biocompute Name, Version, and URL not formatted as expected: {}".format(e))
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if bco_url in bcos:
                # Other version of this BCO object exists
                current_version = bcos[bco_url]["bco_version"]

                if semver.compare(bco_id_version, current_version, key=coerce):
                    # New one is newer version, set:
                    bcos[bco_url] = {
                            "bco_name"   : bco_id_name,
                            "bco_version": bco_id_version,
                            "bco_object" : p
                            }

                else:
                    # Do nothing
                    pass
            else:
                # Not in dictionary yet
                bcos[bco_url] = {
                        "bco_name"   : bco_id_name,
                        "bco_version": bco_id_version,
                        "bco_object" : p
                        }
        for key, value in bcos.items():
            # unique_published.append(value["bco_object"])
            # import pdb;pdb.set_trace()
            unique_published.add(value["bco_object"]["id"])

        # result_list = chain(user_objects.intersection(prefix_objects).values(*return_values), unique_published(*return_values))
        unique_published = bco.objects.filter(id__in=unique_published)
        result_list = chain(user_objects.intersection(unique_published).values(*return_values), prefix_objects.values(*return_values))

        return Response(
                data=result_list,
                status=status.HTTP_200_OK
                )

