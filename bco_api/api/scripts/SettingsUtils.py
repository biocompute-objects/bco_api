# Utilities
from . import FileUtils

# For loading schema.
import jsonref

# For testing only.
import json
import os

class SettingsUtils:

    # Class Description
    # -----------------

    # These are methods for initializing the program.


    # Load the settings file.
    def load_settings_file(self, file_path):

        # file_path: the file to read for settings.

        return FileUtils.FileUtils().read_conf_file(
            file_location = file_path, 
            keys = {
                'HOSTNAMES': 'list', 
                'OBJECT_NAMING': 'dict', 
                'REQUESTS': 'dict', 
                'VALIDATIONS': 'dict', 
                'DATA_MODES': 'dict'
            }
        )


    # Load the request templates.
    def load_schema_old(self):

        # No arguments.

        # Search the templates folder for files ending in '.schema'.
        schema_files = FileUtils.FileUtils().find_files('request_definitions/', '*.schema')
        print(schema_files)
        # Create a dictionary to return all the schema.
        returning = {'DELETE': {}, 'GET': {}, 'PATCH': {}, 'POST': {}}

        # Parse into different types.
        '''
        for file in schema_files:

            # Split on '_', and use the first entry as the request type and
            # the second entry as the template.

            # Use the file names to infer the function of the schema, NOT
            # the 'title' field within the schema, as this cannot be
            # guaranteed to be unique.
            split_up = file.split('/')[-1].split('.')[0]
            request_type = split_up.split('_')[0]
            request_template = '_'.join(split_up.split('_')[1:])

            # Read the schema and use the title as the sub-key.
            with open(file, mode='r') as f:
                request_schema = json.load(f)

            # Now update our returnable.
            returning[request_type][request_template] = request_schema
        '''
        for file in schema_files:

            # We need to split the path to find 1) the absolute directory path
            # so that we can use $ref properly, and 2) so that we can determine
            # the type of request type (DELETE, GET, PATCH, POST).

            # Split on the directory breakers.
            split_up = file.split('/')

            # Find the absolute path.
            absolute_path = '/'.join(split_up[:len(split_up)-1])

            # Find the request type.
            # Split on '.' and use the first entry as the request type.
            request_type = split_up[-1].split('.')[0]

            print(absolute_path)
            print(request_type)

            # Now load the schema WITH references.
            # Source: modified from https://medium.com/grammofy/handling-complex-json-schemas-in-python-9eacc04a60cf

            # Set the value.
            with open(file, mode='r') as f:
                #returning[request_type] = json.load(f)
                returning[request_type] = jsonref.loads(f.read(), base_uri='file://{}/'.format(absolute_path), jsonschema=True)

        # Return the templates.
        #print(json.dumps(returning, indent=4, sort_keys=True))

        return returning


    # Create a dictionary to hold schema information.
    def load_schema_local(self, search_parameters, mode):

        # search_parameters: dictionary of file search locations and file endings.

        # mode: loading for requests or for validation?

        # A more advanced version of this would set the schema $id based on
        # where the schema resides, negating the need for manual entry of the $id.

        # Define a dictionary to hold top-level folder/file information.
        schema = {}

        # Iterate over the search parameters.
        for folder, extension in search_parameters.items():
            raw_files = FileUtils.FileUtils().get_folder_tree_by_extension(search_folder=folder, search_extension=extension)

            # We now have the files, so load the schema.

            # First, initialize schema.
            schema[folder] = {}

            # Now go over each path.
            for current_file in raw_files['paths']:

                # We can now set keys.
                with open(current_file, mode='r') as f:
                    schema[folder][current_file] = json.load(f)
                    
                    # Set the id.
                    schema[folder][current_file]['$id'] = 'file:' + current_file
                    
        
        #print('PRE-PROCESSED-----------')
        #print(json.dumps(schema, indent=4))
        #print('=====================================')
        # Now go through and define the absolute reference paths.
        # We have to do this recursively as we do not know
        # where we will see "$ref$.

        # The jsonschema library does NOT support relative references
        # within the document, see https://json-schema.org/understanding-json-schema/structuring.html#using-id-with-ref
        # Therefore, we must manually resolve the paths.  This is actually
        # a stronger solution, however, as it allows for referencing
        # schema anywhere within the project directory as opposed to
        # referencing schema within the same folder level only (as is
        # the case with the relative reference examples given at the link above).

        # The schema_files are separated at the top level
        # by the folders provided in search_parameters.

        # Source: https://stackoverflow.com/questions/10756427/loop-through-all-nested-dictionary-values
        def set_refs(d, root_folder):

            # Set the keys.
            if '$ref' in d:

                # If the reference is internal to the document, ignore it.
                # Otherwise, define the reference.
                if d['$ref'][0] != '#':
                    d['$ref'] = 'file:' + os.getcwd() + '/' + root_folder + d['$ref']
                    #d['$ref'] = 'http://127.0.0.1:8000/' + root_folder + d['$ref']
                    #print(os.listdir())

            for k, v in d.items():
                if isinstance(v, dict):
                    set_refs(v, root_folder)

            # Kick it back.
            return(d)

        # A more advanced implementation would allow for referencing schema
        # outside of the hosting folder.

        # Are we defining for requests or for validations?
        
        if mode == 'requests':

             # Call set refs by each top-level folder.
            for folder, contents in schema.items():
                schema[folder] = set_refs(schema[folder], root_folder='api/')

        elif mode == 'validations':

            # Call set refs by each top-level folder.
            for file, contents in schema['validation_definitions/'].items():

                # Split the file name up to help construct the root folder.
                file_name_split = file.split('/')

                # Where is the 'validation_definitions/' item?
                vd_index = file_name_split.index('validation_definitions')

                # Collapse everything after this index but before the file name.
                collapsed = '/'.join(file_name_split[vd_index+1:len(file_name_split)-1]) + '/'

                # Set the name.
                schema['validation_definitions/'][file] = set_refs(schema['validation_definitions/'][file], root_folder='api/validation_definitions/' + collapsed)

            #print(json.dumps(schema, indent=4, sort_keys=True))

        # Return the public-facing schema AND the processed schema?
        return schema


    # Define the schema for each request type.
    def define_request_schema(self, schema):

        # schema: everything found in self.load_local_schema.

        # Create a dictionary to return all the request types.
        returning = {'DELETE': {}, 'GET': {}, 'PATCH': {}, 'POST': {}}

        # Now go through the schema to locate the request information.
        for k, v in schema.items():

            # If the object title is a given request type, update returning.
            if v['title'] == 'DELETE':
                returning['DELETE'] = v
            elif v['title'] == 'GET':
                returning['GET'] = v
            elif v['title'] == 'PATCH':
                returning['PATCH'] = v
            elif v['title'] == 'POST':
                returning['POST'] = v

        # Kick it back.
        return returning



































    # --- USER METHODS --- #








































    # Here are methods for updating fields in the loaded schema.
'''
    # Create regex to update schema fields.
    def create_regex(self):

        # Valid prefixes for URIs.
        BCO_PREFIXES = ['https', 'ftp', 'doi', 'http']

        # The URI to use for the creation of new BCOs.
        BCO_ROOT = 'nih.gov'

        # The URI tag for the creation of new BCOs.
        BCO_TAG = 'NIH'

        # Schema/URI mappings.
        SCHEMA_URI_MAPPINGS = {'IEEE 2791-2020': 'https://w3id.org/ieee/ieee-2791-schema/2791object.json'}

        # USER-DEFINED SCHEMA

        # Define valid regexs for BCOs.
        BCO_REGEX = ['^' + prefix + '://' + BCO_ROOT + '/' + BCO_TAG + '_(\d+)_v_(\d+)$' for prefix in BCO_PREFIXES]
        BCO_REGEX.append('^NEW$')
        BCO_REGEX = '|'.join(BCO_REGEX)

        # Define valid regexs for schema.
        SCHEMA = []

        for schema, uri in SCHEMA_URI_MAPPINGS.items():
            SCHEMA.append(schema)

        SCHEMA_REGEX = '|'.join(['^' + schema + '$' for schema in SCHEMA])

        # Create variables for accessing the schema from within other files.
        POST_REQUEST_SCHEMA = ''
        GET_REQUEST_SCHEMA = ''
        PATCH_REQUEST_SCHEMA = ''
        DELETE_REQUEST_SCHEMA = ''

        # Set the schema files so that we can define POST, GET, PATCH, and DELETE requests.
        for request_type in ['POST', 'GET', 'PATCH', 'DELETE']:

            # Open the file for this request type.
            with open('./api/request_definitions/' + request_type + '.schema', mode='r') as f:

                # Create a variable to hold the JSON.
                json_helper = json.load(f)

                # Update the schema based on the request type.
                if request_type == 'POST':

                    # Acceptable BCO patterns.
                    json_helper['items']['properties']['object_id']['pattern'] = BCO_REGEX

                    # Acceptable schema patterns.
                    json_helper['items']['properties']['schema']['pattern'] = SCHEMA_REGEX

                    # Set the schema.
                    POST_REQUEST_SCHEMA = json_helper

                elif request_type == 'GET':
                    print('hi')
                elif request_type == 'PATCH':
                    print('hi')
                elif request_type == 'DELETE':
                    print('hi')

            # Dump to the file with the updated values (optional).
            with open('./api/request_definitions/' + request_type + '.schema', mode='w') as f:

                # Dump.
                json.dump(json_helper, f)

    # Update the request templates with provided regex.
    def update_request_templates(self):
        print('hi')
'''

