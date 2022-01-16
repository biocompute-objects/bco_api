# BCOs
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
import semver
from semver import VersionInfo as Version
from typing import Optional, Tuple

# TODO: This is repeated code, should consolidate
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


def POST_api_objects_published():
    """
    Get All published objects (publicly available)
    """

    published = bco.objects.filter(state='PUBLISHED').values()
    unique_published = []

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
        import pdb; pdb.set_trace()
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
        unique_published.append(value["bco_object"])

    return Response(
            data=unique_published,
            status=status.HTTP_200_OK
            )
