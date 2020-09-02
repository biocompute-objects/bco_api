
# Security Policy

The security policy for the server is based on an institution-group-user model.  This means that every user is part of a group and every group is part of an institution.  Of course, there can be multiple institutions, multiple groups in each institution, and multiple users in each group.  Also, users can be part of multiple groups.  But institutions are considered completely separate from the point of view of the security policy.

For example, say we are a researcher named Mrs. Smith and we split our research duties between three groups.  The first is NCI Genomics at NIH, the second is Pharma Development at NIH, and the third is Bioinformatics-GlyGen at George Washington University.  Then in this case, we are part of two institutions but three groups - each of which may have different permissions.

**When should I set up a group?**

In general, each lab, team, or research unit should have a group.  But the customization won't necessarily stop there.  For example, certain platforms that automatically generate JSON, such as Galaxy, can be assigned to a group that has publish permissions.  In essence, any user or platform that needs to generate JSON should be assigned a group and group inclusion should be as restrictive as possible.  This means that all users in the group should share some common purpose or have some common need to justify their permissions.

# The security.policy file

The api/security_policy/security.policy file is the master permissions list for an API installation.  Although you can edit permissions in Django admin, from a technical point of view, this file is the master record that you are actually writing to.  **The security.policy file should never be manually written to.  It is presented here to show how permissions are stored internally.  Always use the admin tool to change permissions!**

Permissions are assigned using the principle of "explicit is better than implicit".  This means that a user's default permissions are none, and only permissions specified in the security.policy file are assigned to the user.  A standard permissions directive is formatted as follows,

institution_name group_name database_name table_name object_class object_name operation field_specifier

Each of these components is explained in the following table.

||institution_name | group_name | database_name | table_name | object_class | object_name | operation | field_specifier
------------ | ------------ | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | -------------
description | The associated institution(s) | The group(s) within that(those) institution(s) | The specific API database(s) | The specific table(s) | The "class(es)" of objects (see below) | The name(s) of the objects within a given class | The operation(s) | The field(s) to apply the operation to
values | Any string | Any string | Any extant database | Any extant table | Any extant object class | Any extant object name within that class | Any combination of ALL, DELETE, GET, PATCH, POST | Any extant field within the named object

The format is as follows.<br/>
<br/>

**security.policy file contents**

INSTITUTIONS<br/>
institution_name_1<br/>
institution_name_2<br/>
institution_name_3<br/>
...<br/>

GROUPS<br/>
institution_name group_name_1<br/>
institution_name group_name_2<br/>
institution_name group_name_3<br/>
...<br/>

USERS<br/>
institution_name group_name username_1<br/>
institution_name group_name username_2<br/>
institution_name group_name username_3<br/>
...<br/>

PERMISSIONS<br/>
institution_name group_name database_name table_name object_class object_name permission_type [ALL, DELETE, GET, PATCH, POST] field_specifier<br/>
institution_name group_name database_name table_name object_class object_name permission_type [ALL, DELETE, GET, PATCH, POST] field_specifier<br/>
institution_name group_name database_name table_name object_class object_name permission_type [ALL, DELETE, GET, PATCH, POST] field_specifier<br/>
...<br/>

**Example settings.policy file**

INSTITUTIONS<br/>
GWU<br/>
FDA<br/>
NIH<br/>

GROUPS<br/>
GWU HIVE<br/>
GWU medschool<br/>
FDA pharmaapproval<br/>
NIH NCI-genomics<br/>

USERS<br/>
GWU HIVE chrisarmstrong<br/>
GWU HIVE hadleyking<br/>
GWU medschool misterdoctor<br/>
FDA pharmaaproval msresearcher<br/>
NIH NCI-genomics seniorresearcher<br/>

PERMISSIONS<br/>
GWU HIVE ALL ALL ALL [ALL] ALL [ALL]<br/>
GWU HIVE BCOs GlyGen published_objects [ALL] ALL [ALL]<br/>
GWU medschool BCOs Galaxy drafted_objects [ALL] [GET] [contributors]<br/>
GWU medschool BCOs Galaxy published_objects [https://object1.org/v-1, https://object2.org/v-2] DELETE [ALL]<br/>
FDA pharmaapproval Recipes HIVE drafted_objects ALL PATCH [authors.main, contributors.main]<br/>
FDA [pharmareviewers, labauditors, seniorresearchers] WetLabAnalytics analytics_results [POST] [https://fda.gov/[^objects_(d+)]/v/(d+)] 
NIH NCI-genomics patient_records current ongoing_research [ALL] [GET, PATCH, POST] [patient.name, patient.status, patient.history[].procedures]<br/>

**Explanation of Permissions**

Institution | Group | Database | Table | Object Class | Object Name | Operation | Object Fields
------------ | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | -------------
GWU | HIVE | All databases | All tables | All classes | All objects within class | All operations | All fields
