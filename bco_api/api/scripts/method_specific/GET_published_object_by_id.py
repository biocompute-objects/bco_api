# The BCO model
from ...models import bco

# Responses
from rest_framework import status
from rest_framework.response import Response


def GET_published_object_by_id(oi_root):
    """
    Get a published object given a root.

    See if the root ID even exists.

    We have to query twice because we don't
    have a field in the bco model to hold
    the object version...

    Note the trailing slash in the regex search to prevent
    sub-string matches (e.g. http://127.0.0.1:8000/BCO_5 and
    http://127.0.0.1:8000/BCO_53 would both match the regex
    http://127.0.0.1:8000/BCO_5 if we did not have the trailing
    slash).

    """
    oi_root = oi_root.split("_")[0] + '{:06d}'.format(int(oi_root.split("_")[1]))
    all_versions = list(
        bco.objects.filter(
            object_id__regex=rf'(.*?)/{oi_root}/',
            state='PUBLISHED'
        ).values_list(
            'object_id',
            flat=True
        )
    )

    # Get the latest version for this object if we have any.
    if len(all_versions) > 0:

        # There was at least one version of the root ID,
        # so now perform some logic based on whether or
        # not a version was also passed.

        # First find the latest version of the object.
        latest_major = 0
        latest_minor = 0

        latest_version = [
            i.split('/')[-1:][0] for i in all_versions
        ]

        for i in latest_version:

            major_minor_split = i.split('.')

            if int(major_minor_split[0]) >= latest_major:
                if int(major_minor_split[1]) >= latest_minor:
                    latest_major = int(major_minor_split[0])
                    latest_minor = int(major_minor_split[1])

        # Kick back the latest version.
        return Response(
            data=bco.objects.filter(
                object_id__regex=rf'{oi_root}/{latest_major}.{latest_minor}',
                state='PUBLISHED'
            ).values_list(
                'contents',
                flat=True
            ),
            status=status.HTTP_200_OK
        )

    else:

        # If all_versions has 0 length, then the
        # the root ID does not exist at all.
        print('No objects were found for the root ID provided.')
        return Response(
            data='No objects were found for the root ID provided.',
            status=status.HTTP_400_BAD_REQUEST
        )
