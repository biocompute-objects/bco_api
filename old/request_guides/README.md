# Request Guides

Each of the 4 different request types (POST, GET, PATCH, DELETE) has defined request templates which can be viewed in each of these guides.  Each request template is defined using a schema and in general the following response codes apply to all request types.

#### Return Codes (shared across DELETE, GET, PATCH, and POST requests)

Code | Description | Payload
------------ | ------------ | ------------
400 | the formulated request did not match its corresponding request schema | The schema for the request type
401 | the request requires user authentication which was not provided | string
403 | the request cannot be completed because the requesting user does not have permission to make the request | string

### [DELETE Templates](./delete.md)
### [GET Templates](./get.md)
### [PATCH Templates](./patch.md)
### [POST Templates](./post.md)
