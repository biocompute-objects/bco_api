def GET_validate_payload_against_schema(bulk_request):

	# Take the bulk request and determine which
	# kind of schema we're looking for.

	# First, get the object to be validated.
	to_be_validated = bulk_request['payload']

	# Is the schema on the server or was it provided?
	if 'schema_server' in bulk_request:
		
		# Load the schema, then pass it along for validation.
		# Check to make sure schema file exists...
		return JsonUtils.JsonUtils().check_object_against_schema(object_pass=to_be_validated, schema_pass=json.load('./validation_definitions/' + bulk_request['schema_server']))

	elif 'schema_own' in bulk_request:
		
		# Use the provided schema.
		return JsonUtils.JsonUtils().check_object_against_schema(object_pass=to_be_validated, schema_pass=bulk_request['schema_own'])