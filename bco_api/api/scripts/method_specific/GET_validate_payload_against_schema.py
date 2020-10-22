import json
from .. import JsonUtils

def GET_validate_payload_against_schema(bulk_request):

	# Take the bulk request and determine which
	# kind of schema we're looking for.

	# Since bulk_request is an array, go over each
	# item in the array, stopping if we have a failure.
	for validation_object in bulk_request:

		# First, get the object to be validated.
		to_be_validated = validation_object['payload']

		# Is the schema on the server or was it provided?
		if 'schema_server' in validation_object:
			
			print('+=+=+=+=++=+=+=+=+=++=+=+=+=++=+=+=+=++=+=+=+=++=+=+=+=++=+=+=+')
			# Load the schema, then pass it along for validation.
			# Check to make sure schema file exists...
			with open('api/validation_definitions/' + validation_object['schema_server'], 'r') as f:
				schema_helper = json.load(f)

			return JsonUtils.JsonUtils().check_object_against_schema(object_pass=to_be_validated, schema_pass=schema_helper)

		elif 'schema_own' in bulk_request:
			
			# Use the provided schema.
			return JsonUtils.JsonUtils().check_object_against_schema(object_pass=to_be_validated, schema_pass=validation_object['schema_own'])