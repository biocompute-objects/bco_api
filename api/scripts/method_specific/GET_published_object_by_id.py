# The BCO model
from api.models import BCO

# Responses
from rest_framework import status
from rest_framework.response import Response

# Below is helper code to deal with how we are allowing non standard versions (i.e. 1.2 instead of 1.2.0, etc).
import re
from semver import VersionInfo as Version
from typing import Optional, Tuple

# TODO: This should be put into a universal place to grab from - also duplicated in POST_api_objects_drafts_token.py

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
    rest = match.string[match.end() :]  # noqa:E203
    return ver, rest


def GET_published_object_by_id(oi_root):
    """
    Get a published object given a root.

    See if the root ID even exists.

    We have to query twice because we don't
    have a field in the BCO model to hold
    the object version...

    Note the trailing slash in the regex search to prevent
    sub-string matches (e.g. http://127.0.0.1:8000/BCO_5 and
    http://127.0.0.1:8000/BCO_53 would both match the regex
    http://127.0.0.1:8000/BCO_5 if we did not have the trailing
    slash).

    """

    # Note: This is not needed - removing out the underscore breaks the regex below, leaving in for the moment
    #       since I'm not sure why it was ever added (maybe there is a reason?)
    # oi_root = oi_root.split("_")[0] +  '{:06d}'.format(int(oi_root.split("_")[1]))
    all_versions = list(
        BCO.objects.filter(
            object_id__regex=rf"(.*?)/{oi_root}/", state="PUBLISHED"
        ).values_list("object_id", flat=True)
    )

    # Get the latest version for this object if we have any.
    if len(all_versions) > 0:

        # There was at least one version of the root ID,
        # so now perform some logic based on whether or
        # not a version was also passed.

        # First find the latest version of the object.
        latest_version = [i.split("/")[-1:][0] for i in all_versions]
        l_version, _ = coerce(max(latest_version, key=coerce))

        # Kick back the latest version.
        return Response(
            data=BCO.objects.filter(
                object_id__regex=rf"{oi_root}/{l_version.major}.{l_version.minor}?.?{l_version.patch}",
                state="PUBLISHED",
            ).values_list("contents", flat=True),
            status=status.HTTP_200_OK,
        )

    else:

        # If all_versions has 0 length, then the
        # the root ID does not exist at all.
        print("No objects were found for the root ID provided.")
        return Response(
            data="No objects were found for the root ID provided.",
            status=status.HTTP_404_NOT_FOUND,
        )
