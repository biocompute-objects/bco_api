
# Security Policy

The security policy for the server is based on an institution-group-user model.  This means that every user is part of a group and every group is part of an institution.  Of course, there can be multiple institutions, multiple groups in each institution, and multiple users in each group.  Also, users can be part of multiple groups.  But institutions are considered completely separate from the point of view of the security policy.

For example, say we are a researcher named Mrs. Smith and we split our research duties between three groups.  The first is NCI Genomics at NIH, the second is Pharma Development at NIH, and the third is Bioinformatics-GlyGen at George Washington University.  Then in this case, we are part of two institutions but three groups - each of which may have different permissions.

# The security.policy file

The api/security_policy/security.policy file is the master permissions list for an API installation.  Although you can edit permissions in Django admin, from a technical point of view, this file is the master record that you are actually writing to.  **The security.policy file should never be manually written to.  It is presented here to show how permissions are stored internally.  Always use the admin tool to change permissions!**

The format is as follows.
&nbsp;

**security.policy file contents**

INSTITUTIONS
institution_name_1
institution_name_2
...
institution_name_n

GROUPS
institution_name group_name_1
institution_name group_name_2
...
institution_name group_name_n

USERS
institution_name group_name username
institution_name group_name username
...
institution_name group_name username

PERMISSIONS
institution_name group_name_1 database_name table_name object_class object_name permission_type [ALL, DELETE, GET, PATCH, POST] field_specifier
&nbsp;

**Example settings.policy file**

INSTITUTIONS
GWU
FDA
NIH

GROUPS
GWU HIVE
GWU medschool
FDA pharmaapproval
NIH NCI-genomics

USERS
GWU HIVE chrisarmstrong
GWU HIVE hadleyking
GWU medschool misterdoctor
FDA pharmaaproval msresearcher
NIH NCI-genomics seniorresearcher

PERMISSIONS
GWU HIVE ALL ALL ALL \[ALL\] ALL [ALL]
GWU HIVE BCOs GlyGen published_objects [ALL] ALL [ALL]
GWU medschool BCOs Galaxy drafted_objects [ALL] [GET] [contributors]
GWU medschool BCOs Galaxy published_objects [https://object1.org/v-1, https://object2.org/v-2] DELETE [ALL]
FDA pharmaapproval Recipes HIVE drafted_objects ALL PATCH [authors.main, contributors.main]
NIH NCI-genomics patient_records current ongoing_research [ALL] [GET, PATCH, POST] [patient.name, patient.status, patient.history[].procedures]
&nbsp;

**Explanation of Permissions**
Institution | Group | Database | Table | Object Class | Object Name | Operation | Object Fields
------------ | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | -------------
GWU | HIVE | All databases | All tables | All classes | All objects within class | All operations | All fields
