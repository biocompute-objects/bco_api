# DELETE Request Templates

<br/>

## Request Template:  Delete object(s)

#### Request Type:  Array with JSON objects

Field | Description | Type | Allowable Values | Optional
------------ | ------------ | ------------ | ------------- | -------------
table | the table to delete the objects in | string | any of the table names in models.py | no
object_id | the ID of the object to delete | string | any string matching the regex defined in bco_api/request_definitions/DELETE.schema| no
state | the state of the objects to delete | string | "DRAFT" or "PUBLISHED" | yes

### Note: A DELETE request only marks an object for deletion.  A second DELETE request must be sent for the same object to delete it.  The second request must occur within 1 minute of the first DELETE request in order to go through.  Otherwise, the object state is reverted back to non-deletable.

#### Return Codes

Code | Description | Payload
------------ | ------------ | ------------
200 | all object_id with state in table have been marked for deletion (time-sensitive, see above) | JSON of object_ids that will be deleted upon secondary request
404 | an object_id with the given state could not be found in the provided table | string
410 | all object_id with state in table have been deleted | string

#### Example Request (Console)

```
fetch('http://127.0.0.1:8000/bco/objects/delete/', {
  method: 'DELETE',
  body: JSON.stringify([
  	{
	    table: "glygen",
	    object_id: "New",
	    state:  "DRAFT"
	  },
	  {
	    table: "oncomx",
	    object_id: "A",
	    state: "PUBLISHED"
	  }
  ]),
  headers: {
    'Content-type': 'application/json; charset=UTF-8'
  }
})
.then(res => res.json())
.then(console.log)
```

#### Example Response (Console)

```
Get from console...
```