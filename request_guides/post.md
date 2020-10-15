# POST Request Templates

<br/>

## Request Template:  Create new object

#### Request Type:  Array with JSON objects

Field | Description | Type | Allowable Values | Optional
------------ | ------------ | ------------ | ------------- | -------------
template | the name of the request template | string | "CREATE" | no
table | the table to write the new object to | string | any of the table names in models.py | no
object_id | either 'NEW' or an existing ID in the repository | string | any string matching the regex defined in bco_api/request_definitions/POST.schema| no
schema | the schema under which the POSTed object falls | string | any URI or string matching the regex defined in validation_definitions| no
payload | the JSON contents to be stored | JSON | any valid JSON | no
state | the state of the object | string | "DRAFT" or "PUBLISHED"| no

#### Example Request (Console)

```
fetch('http://127.0.0.1:8000/bco/objects/create/', {
  method: 'POST',
  body: JSON.stringify([
  	{
	    table: "glygen",
	    object_id: "New",
	    schema: "FDSA",
	    bco: "{\"file test stuff\": \"here\"}",
	    state:  "DRAFT"
	  },
	  {
	    table: "oncomx",
	    object_id: "A",
	    schema: "IEEE 2791-2020",
	    bco: "{\"file test stuff\": \"here\"}",
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

## Request Template:  Convert payload to schema

#### Request Type:  Array with JSON objects

Field | Description | Type | Allowable Values | Optional
------------ | ------------ | ------------ | ------------- | -------------
destination_table | the table to write the object to | string | any of the table names in models.py | no
destination_id | the object ID for the converted object | string | any object ID matching the regex requirements in settings.py | no
schema | the schema under which the POSTed NEW object falls | string | any URI or string matching the regex defined in validation_definitions | no
payload | the JSON contents to be stored | JSON | any valid JSON | no
state | the state of the object | string | "DRAFT" or "PUBLISHED" | no

Note: source_table and source_id must both be provided if converting an existing object.

#### Example Request (Console)

```
fetch('http://127.0.0.1:8000/bco/objects/create/', {
  method: 'POST',
  body: JSON.stringify([
  	{
	    table: "glygen",
	    object_id: "New",
	    schema: "FDSA",
	    bco: "{\"file test stuff\": \"here\"}",
	    state:  "DRAFT"
	  },
	  {
	    table: "oncomx",
	    object_id: "A",
	    schema: "IEEE 2791-2020",
	    bco: "{\"file test stuff\": \"here\"}",
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

## Request Template:  Convert existing object between schemas

#### Request Type:  Array with JSON objects

Field | Description | Type | Allowable Values | Optional
------------ | ------------ | ------------ | ------------- | -------------
source_table | the table from which to get the source object | string | any of the table names in models.py | no
source_id | the object ID in the source table | string | any existent object ID | no
destination_table | the table to write the object to | string | any of the table names in models.py | no
destination_id | the object ID for the converted object | string | any object ID matching the regex requirements in settings.py | no
schema | the schema under which the POSTed NEW object falls | string | any URI or string matching the regex defined in validation_definitions | no
payload | the JSON contents to be stored | JSON | any valid JSON | no
state | the state of the object | string | "DRAFT" or "PUBLISHED" | no

Note: source_table and source_id must both be provided if converting an existing object.

#### Example Request (Console)

```
fetch('http://127.0.0.1:8000/bco/objects/create/', {
  method: 'POST',
  body: JSON.stringify([
  	{
	    table: "glygen",
	    object_id: "New",
	    schema: "FDSA",
	    bco: "{\"file test stuff\": \"here\"}",
	    state:  "DRAFT"
	  },
	  {
	    table: "oncomx",
	    object_id: "A",
	    schema: "IEEE 2791-2020",
	    bco: "{\"file test stuff\": \"here\"}",
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

## Request Template:  Validate payload against schema

#### Request Type:  Array with JSON objects

Field | Description | Type | Allowable Values
------------ | ------------ | ------------ | -------------
payload | the JSON contents to be stored | JSON | any valid JSON
schema | the schema to validate against | string | any URI or string matching the regex defined in validation_definitions

#### Example Request (Console)

```
fetch('http://127.0.0.1:8000/bco/objects/create/', {
  method: 'POST',
  body: JSON.stringify([
  	{
	    table: "glygen",
	    object_id: "New",
	    schema: "FDSA",
	    bco: "{\"file test stuff\": \"here\"}",
	    state:  "DRAFT"
	  },
	  {
	    table: "oncomx",
	    object_id: "A",
	    schema: "IEEE 2791-2020",
	    bco: "{\"file test stuff\": \"here\"}",
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

## Request Template:  Start/Stop API logging

#### Request Type:  JSON Object

Field | Description | Type | Allowable Values
------------ | ------------ | ------------ | -------------
logging | field describing logging command | string | "START" or "STOP"

#### Example Request (Console)

```
fetch('http://127.0.0.1:8000/bco/objects/create/', {
  method: 'POST',
  body: JSON.stringify([
  	{
	    logging: "START"
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
