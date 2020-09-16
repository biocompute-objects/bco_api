# GET Request Templates

<br/>

## Request Template:  Retrieve object(s)

#### Request Type:  Array with JSON objects

Field | Description | Type | Allowable Values | Optional
------------ | ------------ | ------------ | ------------- | -------------
table | the table to retrieve the objects from | string | any of the table names in models.py | no
object_id | the ID of the object to delete | string | any string matching the regex defined in GET.schema | no
fields | the fields within the object to retrieve | string | any string matching the regex defined in GET.schema | no
state | the state of the object | string | "DRAFT" or "PUBLISHED"| yes

#### Example Request (Console)

```
fetch('http://127.0.0.1:8000/bco/objects/delete/', {
  method: 'DELETE',
  body: JSON.stringify([
    {
	    table: "glygen",
	    object_id: "New",
	    fields: "ALL",
	    state:  "DRAFT"
	  },
	  {
	    table: "oncomx",
	    object_id: "A",
            fields: [
                'description_domain',
                'provenance_domain',
                'extension_domain.authors.contributors'
            ]
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

<br/>

## Request Template:  Retrieve available schema(s)

#### Request Type:  JSON object

Field | Description | Type | Allowable Values | Optional
------------ | ------------ | ------------ | ------------- | -------------
schemas | filler field | string | "ALL" | no

#### Example Request (Console)

```
fetch('http://127.0.0.1:8000/bco/objects/delete/', {
  method: 'DELETE',
  body: JSON.stringify(
    {
    	schemas: "ALL"
    }
  ),
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
