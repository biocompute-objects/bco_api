# For creating BCO IDs.
from django.conf import settings

# For retrieving objects.
from ..models import bco_object
from ..serializers import BcoGetSerializer

class DbUtils:

    # Class Description
    # -----------------

    # These methods are for interacting with our sqlite database.

    # Generate unique object IDs.
    def generate_object_id(self, existing_id=False, version_flag=False):

        # Arguments
        # ---------

        #  existing_id:  an ID that is passed for version updating.

        # version_flag:  if true, we don't need a completely new
        #                object ID, we just need potentially need a new version.
        #                We say potentially need because if existing_id doesn't
        #                exist in the database, then we'll just use existing_id
        #                as the new ID.

        # First, get all BCOs.  These objects are returned as JSON, so
        # we can work with them more easily.
        bco_objects = BcoGetSerializer(bco_object.objects.all(), many=True).data

        print('HERE')
        print(bco_objects)
        print('THERE')
        # Completely new object or just a new version?
        if version_flag is False:

            # Do we have anything?
            if len(bco_objects) > 0:

                # Get all the IDs.

                # Define a list to hold the object IDs.
                bco_object_ids = []

                # Now go through each object and get its ID.
                for current_object in bco_objects:

                    # Extract and append the object ID.
                    bco_object_ids.append(current_object['object_id'])

                # Define a variable to keep track of the maximum
                # number found so far as we go through the object IDs.
                max_number = -1

                # We want to see what the most react object number is.
                for current_object_id in bco_object_ids:

                    # Split on '/', keeping only the last (non-URI) part.
                    split_up = current_object_id.split('/')[-1]

                    # Split again and keep the number.
                    # Note the type conversion from string to int.
                    split_up = int(split_up.split('_')[1])

                    # Is this greater than our current maximum?
                    if split_up > max_number:
                        max_number = split_up

                # Increment the max number and stringify.
                new_number = str(max_number + 1)

                # Create the brand-new object.
                created_id = 'https://' + settings.BCO_ROOT + '/' + settings.BCO_TAG + '_' + new_number + '_v_1'

            else:

                # No objects, so just construct a new one.
                created_id = 'https://' + settings.BCO_ROOT + '/' + settings.BCO_TAG + '_1_v_1'

        else:

            # We may just need a new version of the 'same' object.

            # Get the current version number.
            # Note the type conversion from string to int.
            current_version_number = existing_id.split('/')[-1]
            current_version_number = int(current_version_number.split('_')[-1])

            # Increment the version number.
            # Note the type conversion from int to string.
            incremented = str(current_version_number + 1)

            # Re-form the ID.
            created_id = existing_id.split('/')
            id_helper = created_id[-1]
            id_helper = id_helper.split('_')
            id_helper[len(id_helper) - 1] = incremented
            id_helper = '_'.join(id_helper)
            created_id[len(created_id) - 1] = id_helper
            created_id = '/'.join(created_id)

            # Does this ID already exist (this is possible when incrementing versions
            # for objects if the requester does not realize they are sending a
            # version of the object that is not the latest one)?

            already_exists_flag = False

            for current_object in bco_objects:

                # Does the object ID already exist?
                if current_object['object_id'] == created_id:
                    already_exists_flag = True

            # Return based on the existence of the created ID.
            if already_exists_flag is False:
                return created_id
            else:
                return 'VERSION_INCREMENT_ERROR'

        # Return our new ID.
        return created_id

    # Retrieve an object from the database.
    def retrieve_object(self, object_id_pass):

        # Arguments
        # ---------

        # object_id_pass:  the ID that we are trying to retrieve.

        try:

            return bco_object.objects.get(object_id=object_id_pass)

        except bco_object.DoesNotExist:

            return 'OBJECT_ID_DOES_NOT_EXIST'

    # Commit a draft BCO.
    def commit_object_draft(self, object_id_pass):

        # Arguments
        # ---------

        # object_id_pass:  the ID that we are committing.
        #                  Committed BCOs cannot be edited.

        # Get the object for this ID.
        retrieved = retrieve_object(object_id_pass=object_id_pass)

        # Serialize the object, but only for the 'state' field.
        # Source:  https://stackoverflow.com/questions/50129567/django-rest-update-one-field

        serializer = BcoGeneralSerializer(retrieved, partial=True)

        # Is the object already committed?
