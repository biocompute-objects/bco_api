# Planned Changes for 24.04 release

## Proposed changes

### Provide `One Click` examples that work for Swagger
- GlyGen and ARGOS do this already. 

### simplify API models and processing
  - previous model was based on multiple DB requests per object and each request could have buld sumissions
  -  We still want bulk submissions but validations and permissions should be checked by classes and serializers before pining DB
#### Examples:
- POST_api_objects_draft_create

### Handeling what will become `Legacy` requests
1. maintain the old code, and not publicize it
2. develope converter functions to process


### Refactor the groups user permissions
- previous model was based on additional objects for Groups and Users,  This required the use of `signals` and meant that there were many additional objects in the DB each time a new user was created. This also led to dependancy issues which prohibits deleting anything. 
- propose to elimiate the extra models

### Refactor the Prefix permission system
- Prefix required it's own two groups and the creation of 5 permissions for each prefix. Look up for authentication was time consuming and taxing on DB. Users also had no idea how to use the system, just what to do to make it work.
- Propose to add `authorized groups` to the prefix model. if it is empty then anyone can use it. If populated than only those in list can use it

### Refactor the BCO permission system
- same situation as prefix

## Permissions

- BCO has `owner`, `auth_group` and `auth_user`
- Prefix has `owner`, and `auth_group` 

## Items to look at later
- `authentication.apis.RegisterUserNoVerificationAPI` has no swagger or tests
- fix email and secrets
- install a `test_template` for Swagger responses
- provide example values that are usable for testing APIs.
- certifying key for prefix as a JWT? 
- owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE, 
- need tests for token
- unwanted swagger endpoints
- need tests for token
- prefix api documentation and portal docs for prefix

Prefix Perms:
	add -> create new DRAFT
	edit -> Change existing Draft
	delete -> Delete Draft
	publish -> Publish Draft
	view -> View/download 
   ONLY if private