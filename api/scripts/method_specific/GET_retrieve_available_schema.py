# For the folder search.
from ..utilities import FileUtils

from ..utilities import JsonUtils
import json

# Put try catch in later to indicate failure to load schema...


def GET_retrieve_available_schema(bulk_request):

    # We don't use settings.VALIDATION_TEMPLATES because
    # that contains paths on the server which we don't
    # want to reveal.

    # Get the schema from the validation_definitions folder.
    folder_schema = FileUtils.FileUtils().get_folder_tree(
        search_folder="validation_definitions/"
    )["paths"]

    # Define a list to hold the processed paths.
    processed_paths = []

    # Strip out everything that is above the server folder level.
    for path in folder_schema:

        # Split the path up to help construct the root folder.
        file_name_split = path.split("/")

        # Where is the 'validation_definitions/' item?
        vd_index = file_name_split.index("validation_definitions")

        # Collapse everything after this index.
        collapsed = "/".join(file_name_split[vd_index + 1 :])

        # Set the name.
        processed_paths.append(collapsed)

    # Create a usable structure.

    # Source: https://stackoverflow.com/questions/9618862/how-to-parse-a-directory-structure-into-dictionary
    dct = {}

    for item in processed_paths:
        p = dct
        for x in item.split("/"):
            p = p.setdefault(x, {})

    return {"request_status": "success", "contents": dct}
