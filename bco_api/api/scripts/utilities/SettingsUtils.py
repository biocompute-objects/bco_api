# Utilities
from . import FileUtils

# For testing only.
import json
import os

# For loading schema.
import jsonref


class SettingsUtils:

    # Class Description
    # -----------------

    # These are methods for initializing the program.

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
            raw_files = FileUtils.FileUtils().get_folder_tree_by_extension(
                search_folder=folder, search_extension=extension
            )

            # We now have the files, so load the schema.

            # First, initialize schema.
            schema[folder] = {}

            # Now go over each path.
            for current_file in raw_files["paths"]:

                # We can now set keys.
                with open(current_file, mode="r") as f:

                    schema[folder][current_file] = json.load(f)

                    # Set the id.
                    schema[folder][current_file]["$id"] = "file:" + current_file

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
            if "$ref" in d:

                # If the reference is internal to the document, ignore it.
                # Otherwise, define the reference.
                if d["$ref"][0] != "#":
                    d["$ref"] = "file:" + os.getcwd() + "/" + root_folder + d["$ref"]

            for k, v in d.items():
                if isinstance(v, dict):
                    set_refs(v, root_folder)

            # Kick it back.
            return d

        # A more advanced implementation would allow for referencing schema
        # outside of the hosting folder.

        # Are we defining for requests or for validations?

        if mode == "requests":

            # Call set refs by each top-level folder.
            for folder, contents in schema.items():
                schema[folder] = set_refs(schema[folder], root_folder="api/")

        elif mode == "validations":

            # Call set refs by each top-level folder.
            for file, contents in schema["validation_definitions/"].items():

                # Split the file name up to help construct the root folder.
                file_name_split = file.split("/")

                # Where is the 'validation_definitions/' item?
                vd_index = file_name_split.index("validation_definitions")

                # Collapse everything after this index but before the file name.
                collapsed = (
                    "/".join(file_name_split[vd_index + 1 : len(file_name_split) - 1])
                    + "/"
                )

                # Set the name.
                schema["validation_definitions/"][file] = set_refs(
                    schema["validation_definitions/"][file],
                    root_folder="api/validation_definitions/" + collapsed,
                )

        # Return the public-facing schema AND the processed schema?
        return schema

    # Define the schema for each request type.
    def define_request_schema(self, schema):

        # schema: everything found in self.load_local_schema.

        # Create a dictionary to return all the request types.
        returning = {"DELETE": {}, "GET": {}, "PATCH": {}, "POST": {}}

        # Now go through the schema to locate the request information.
        for k, v in schema.items():

            # If the object title is a given request type, update returning.
            if v["title"] == "DELETE":
                returning["DELETE"] = v
            elif v["title"] == "GET":
                returning["GET"] = v
            elif v["title"] == "PATCH":
                returning["PATCH"] = v
            elif v["title"] == "POST":
                returning["POST"] = v

        # Kick it back.
        return returning
