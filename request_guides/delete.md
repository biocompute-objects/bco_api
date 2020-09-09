# DELETE Request Templates

<br/>

## Request Template:  Delete object(s)

#### Request Type:  Array with JSON objects

Field | Description | Type | Allowable Values | Optional
------------ | ------------ | ------------ | ------------- | -------------
table | the table to delete the objects in | string | any of the table names in models.py | no
object_id | the ID of the object to delete | string | any string matching the regex defined in DELETE.schema| no
state | the state of the object | string | "DRAFT" or "PUBLISHED"| yes

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
