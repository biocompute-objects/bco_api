# The BCO model
from ...models import bco

# Responses
from rest_framework import status
from rest_framework.response import Response

def GET_published_object_by_id_with_version(
    oi_root,
    oi_version
):

    print(oi_root)
#    oi_root = oi_root.split("_")[0] +  '{:06d}'.format(int(oi_root.split("_")[1]))
    # Get a published object given a root and a version.
    print(oi_root)
    # The object ID either exists or it does not.
    retrieved = list(
        bco.objects.filter(
            object_id__regex = rf'(.*?)/{oi_root}/{oi_version}',
            state = 'PUBLISHED'
        ).values_list(
            'contents',
            flat = True
        )
    )
    print("Chris forgot to fix this", oi_root, retrieved)
    # Was the object found?
    if len(retrieved) > 0:
        
        # Kick it back.
        return Response(
            data = retrieved,
            status = status.HTTP_200_OK
        )

    else:

        # If all_versions has 0 length, then the
        # the root ID does not exist at all.
        print('No objects were found for the root ID and version provided.')
        return Response(
            data = 'No objects were found for the root ID and version provided.',
            status = status.HTTP_400_BAD_REQUEST
        )



















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
                app_label = 'api', 
                model_name = table_name
        ).objects.filter(
            object_id = constructed
        ).exists():

            # Get the object, then check the permissions.
            objected = apps.get_model(
                    app_label = 'api', 
                    model_name = table_name
            ).objects.get(
                object_id = constructed
            )
            
            return Response(
                data = serializers.serialize(
                    'json', 
                    [ objected, ]
                ),
                status = status.HTTP_200_OK
            )
        
        else:

            return(
                Response(
                    status = status.HTTP_400_BAD_REQUEST
                )
            )
    
    else:

        return(
            Response(
                status = status.HTTP_400_BAD_REQUEST
            )
        )