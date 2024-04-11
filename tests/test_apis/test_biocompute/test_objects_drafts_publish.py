#!/usr/bin/env python3

"""Tests for DraftsPublishApi [Bulk Enabled]

DraftsPublishApi:
- checks for legacy submission
- for each object:
 - `user_can_publish_bco`:
   - checks for published_object_id and makes sure it does not exist
   - checks that DRAFT exists
   - if published_object_id in request, then checks that published_object_id version matches BCO version
   - else checks that draft object_id + version does not exist
   - checks if user can publish with prefix of BCO
   : `returns DRAFT object` if every check is passed
  - `parse_and_validate`: validates BCO. If errors then rejected.
  - `publish_draft`:
    - copies draft, assignes new ID and status to the copy
	- updates the "last_update" field in Django and the BCOs "modified" field
	- generates ETag
	- saves published object
	- if "delete_draft" is true then deletes draft
"""