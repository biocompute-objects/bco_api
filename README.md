
# JSON API (BCO API)

This is the repository for the BioCompute Objects API.  Architecturally, the API is separated from any BCO interface (BioCompute Portal, Galaxy, GlyGen, etc...) and can be used with the standard POST, GET, PATCH, and DELETE commands.  The repository comes with an out-of-the-box security policy and can be used within an organization's firewall without much further configuration on the part of the administrator.

# Overview of Repository Contents

The API is built on Django.  Initial setup only involves modifying a few settings and for most users the default security settings should suffice.  The exception to this is the case where an administrator wants their BCOs to be public-facing.  **The server is not secured with any type of API key system!**  If you want to add additional security features you will have to go through the source code and decide what is necessary for your specific installation.  Only files that have been modified or created in addition to the default files of a Django installation are described here.

## Folder Description

```
API
 └─── api (contains the heart of the API)
    └─── library (class definitions)
       └─── DbUtils.py (class for interacting with the SQLite database)
       └─── JsonUtils.py (class for validating JSON)
       └─── RequestUtils.py (class for dealing with requests)
       └─── ResponseUtils.py (class for dealing with responses given by the API)
    └─── request_definitions (schema definitions for each type of request to the API)
       └─── DELETE.schema (the schema definition for a valid DELETE request)
       └─── GET.schema (the schema definition for a valid GET request)
       └─── PATCH.schema (the schema definition for a valid PATCH request)
       └─── POST.schema (the schema definition for a valid POST request)
    └─── validation_definitions* (schema definitions for each type of non-URI validation request)
 └─── api_master (contains top-level project settings)
    └─── settings.py* (where settings such as default object naming and schema registration take place)
    └─── urls.py (pass-through router to the API urls file)
```

\* These files are the only ones that should be manually edited, if at all.

# Quick Start

1.  Clone the repository.  If necessary, add execute permissions to all shell scripts.

```
git clone https://github.com/carmstrong1gw/bco_api
(optional, add execute permissions) sudo some grep commmand +x...
```

2.  Initialize the folder contents (creates virtual environment and adjusts some settings).  At the end of this step, your command line should show an active virtual environment.

```
initialize_api.sh
(should see this after running initialize_api.sh) (env) user@computer:/path/to/json_api$
```

3.  Create a super user (administrator).  Fill in all details as necessary.

```
python3 manage.py createsuperuser
```

4.  Start the server with the shell script.

```
start_server.sh
```

5.  Open up your browser and go to <a href='https://127.0.0.1/8000/admin/' target='_blank'>https://127.0.0.1/8000/admin/</a>.  Log in with the credentials you created in Step 3.  The administrator page is the starting point for controlling any aspect of your installation.  Here is where you can add and delete users, set certain permissions, and 

6.  Right now the only user is the administrator, so you'll want to add at least a test user.  Click on the "Add User" button in the upper right-hand corner of the screen, fill out the fields, then click on "Save" in the lower right-hand corner.

7.  The page that comes up can be used to set attributes of the user, such as first and last name and e-mail address.  You can set these if you'd like, but the main section you want to look at is "Permissions".  Make sure that the user is marked as "Active", but not as "Staff status" or "Superuser status", as these are statuses reserved for users with elevated privileges.

8.  Now that you have a user, you can proceed to set permissions.

# Setting Permissions

The permissions system for the JSON API is quite complex and the full description of its power is given in the LINKsecurityreadme.md.  Here we will be setting some basic permissions for our test user.

to come...

# Create, Read, Update, Delete (CRUD) Requests

The four standard CRUD operations are represented by POST, GET, PATCH, and DELETE.  The 4 URLs that are available to the user for these requests are:

request type | URL | functionalities (templates)
------------ | ------------ | ------------
POST | https://path/to/api/server/payloads/objects/create/ | Create a new object; Convert a JSON object between schemas; Validate a JSON object against a schema
GET | https://path/to/api/server/payloads/objects/read/ | Read objects matching a regex and/or a set of conditions on the object; Retrieve an object chain
PATCH | https://path/to/api/server/payloads/objects/update/ | Update objects matching a regex and/or a set of conditions on the object
DELETE | https://path/to/api/server/payloads/objects/delete/ | Delete objects matching a regex and/or a set of conditions on the object

Each functionality for each type of request is defined in a **request template**.  The requirements for each of these templates are summarized in the tables below.

## POST

#### Request Template:  Create new object

##### Request Type:  Array with JSON objects

JSON Object Requirements

field | description | type | allowable values | optional
------------ | ------------ | ------------ | ------------- | -------------
table | the table to write the object to | string | any of the table names in models.py | no
object_id | either 'NEW' or an existing ID in the repository | string | any string matching the regex defined in POST.schema| no
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

#### Request Template:  Convert payload OR existing object between schemas

##### Request Type:  Array with JSON objects

JSON Object Requirements

field | description | type | allowable values | optional
------------ | ------------ | ------------ | ------------- | -------------
source_table | the table from which to get the source object | string | any of the table names in models.py | yes
source_id | the object ID in the source table | string | any existent object ID | yes
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

#### Request Template:  Validate payload against schema

##### Request Type:  Array with JSON objects

JSON Object Requirements

field | description | type | allowable values
------------ | ------------ | ------------ | -------------
table | the table in which the object_id exists | string | any of the table names in models.py
object_id | either 'NEW' or an existing ID in the repository | string | any string matching the regex defined in POST.schema
schema | the schema to validate against | string | any URI or string matching the regex defined in validation_definitions
payload | the JSON contents to be stored | JSON | any valid JSON

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
