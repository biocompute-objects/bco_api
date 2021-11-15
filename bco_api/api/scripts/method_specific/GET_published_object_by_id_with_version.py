# The BCO model
from ...models import bco

# Responses
from rest_framework import status
from rest_framework.response import Response


def GET_published_object_by_id_with_version(oi_root, oi_version):
    """
    Fetch a published BCO by the PREFIX, BCO NAME, and VERSION ID
    """

    ####
    # We are assuming the oi_root looks something like this
    #       BCO_28
    # Where
    #       `BCO` is the prefix
    # and `28` is the object name
    ####

    # Split by '_'
    underscores = oi_root.count("_")
    if underscores < 1:
        # ERROR - there should be an underscore separating the prefix and the bco name
        return Response(
            data='This API requires that the prefix and the BCO name be separated by an underscore \'_\' in the object_id_root PATH variable.',
            status=status.HTTP_400_BAD_REQUEST
        )

    # TODO: This allows BCO Names to support underscores - not sure if that is valid though
    #       This can be 'fixed' by adding in a check for > 1 above
    #       Might be a better idea to split prefix, bco name, and version into a three part get
    bco_prefix, bco_name = oi_root.split("_", maxsplit=1)

    retrieved = list(
        bco.objects.filter(
            # contents__search=bco_name,
            prefix=bco_prefix,
            contents__provenance_domain__name=bco_name,
            contents__provenance_domain__version=oi_version,
            state='PUBLISHED'
        ).values_list(
            'contents',
            flat=True
        )
    )
    # # The object ID either exists or it does not.
    # retrieved = list(
    #     bco.objects.filter(
    #         object_id__regex = rf'(.*?)/{oi_root}/{oi_version}',
    #         state = 'PUBLISHED'
    #     ).values_list(
    #         'contents',
    #         flat = True
    #     )
    # )
    # Was the object found?
    if len(retrieved) > 0:
        # Kick it back.
        return Response(data=retrieved, status=status.HTTP_200_OK)
    else:
        # If all_versions has 0 length, then the
        # the root ID does not exist at all.
        print('No objects were found for the root ID and version provided.')
        return Response(
            data='No objects were found for the root ID and version provided.',
            status=status.HTTP_400_BAD_REQUEST
        )

    # TODO: This code from here on down appears to be unreachable?  The above if/else will always return the request
    #       Maybe this is placeholder code for something?
    # Instantiate any necessary imports.
    db = DbUtils.DbUtils()

    # First, get the table based on the requested published object.
    table_name = (
            oi_root.split('_')[0] + '_publish'
    ).lower()

    # Does the table exist?
    # TODO: replace with better table call...
    available_tables = settings.MODELS['json_object']

    if table_name in available_tables:

        # Construct the object ID.
        constructed = object_id = settings.PUBLIC_HOSTNAME + '/' + oi_root + '/' + oi_version

        # Does the object exist in the table?
        if apps.get_model(
                app_label='api',
                model_name=table_name
        ).objects.filter(
            object_id=constructed
        ).exists():

            # Get the object, then check the permissions.
            objected = apps.get_model(
                app_label='api',
                model_name=table_name
            ).objects.get(
                object_id=constructed
            )

            return Response(
                data=serializers.serialize(
                    'json',
                    [objected, ]
                ),
                status=status.HTTP_200_OK
            )

        else:

            return (
                Response(
                    status=status.HTTP_400_BAD_REQUEST
                )
            )

    else:

        return (
            Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        )
