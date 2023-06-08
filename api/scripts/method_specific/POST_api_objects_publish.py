#!/usr/bin/env python3
"""Bulk Publish

--------------------
Take the bulk request and publish objects directly.
"""

from api.models import BCO
from api.model.prefix import prefix_table, Prefix
from api.scripts.utilities.DbUtils import DbUtils as db_utils
from api.scripts.utilities.UserUtils import UserUtils as user_utils
from api.scripts.utilities.JsonUtils import parse_bco
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response


def post_api_objects_publish(incoming):
    """
    Take the bulk request and publish objects directly.
    """

    root_uri = settings.OBJECT_NAMING["root_uri"]
    user = user_utils().user_from_request(request=incoming)
    px_perms = user_utils().prefix_perms_for_user(flatten=True, user_object=user)
    bulk_request = incoming.data["POST_api_objects_publish"]
    returning = []
    any_failed = False
    results = {}
    for publish_object in bulk_request:
        try:
            results = parse_bco(publish_object["contents"], results)
        except KeyError as error:
            returning.append(
                db_utils().messages(parameters={"errors": str(error)})[
                    "400_non_publishable_object"
                ]
            )
            any_failed = True
            continue
        object_key = publish_object["contents"]["object_id"]
        if results[object_key]["number_of_errors"] > 0:
            returning.append(
                db_utils().messages(parameters={"errors": results})[
                    "400_non_publishable_object"
                ]
            )
            any_failed = True
            continue

        prefix = publish_object["prefix"].upper()
        if Prefix.objects.filter(prefix=prefix).exists():
            prefix_counter = prefix_table.objects.get(prefix=prefix)

            if "publish_" + prefix in px_perms:
                if "object_id" in publish_object:
                    accession = publish_object["object_id"].split("/")[-2]
                    version = publish_object["object_id"].split("/")[-1]
                    object_num = int(
                        publish_object["object_id"].split("_")[1].split("/")[0]
                    )
                    constructed_obj_id = (
                        root_uri
                        + "/"
                        + accession
                        + "/"
                        + publish_object["contents"]["provenance_domain"]["version"]
                    )
                    if BCO.objects.filter(object_id__contains=accession+'/'+version).exists():
                        # import pdb; pdb.set_trace()
                        returning.append(
                            db_utils().messages(parameters={"object_id": accession+'/'+version})[
                                "409_object_conflict"
                            ]
                        )
                        any_failed = True
                        continue
                    if publish_object["object_id"] != constructed_obj_id:
                        returning.append(
                            db_utils().messages(
                                parameters={
                                    "object_id": publish_object["object_id"],
                                    "constructed_obj_id": constructed_obj_id,
                                }
                            )["409_object_id_conflict"]
                        )
                        any_failed = True
                        continue
                    new_object = {}
                    new_object["contents"] = publish_object["contents"]
                    new_object["object_id"] = constructed_obj_id
                    new_object["contents"]["object_id"] = constructed_obj_id
                    new_object["owner_group"] = publish_object["owner_group"]
                    new_object["owner_user"] = user.username
                    new_object["prefix"] = prefix
                    new_object["last_update"] = timezone.now()
                    new_object["schema"] = "IEEE"
                    new_object["state"] = "PUBLISHED"

                    objects_written = db_utils().write_object(
                        p_app_label="api",
                        p_model_name="BCO",
                        p_fields=[
                            "contents",
                            "last_update",
                            "object_id",
                            "owner_group",
                            "owner_user",
                            "prefix",
                            "schema",
                            "state",
                        ],
                        p_data=new_object,
                    )
                    if prefix_counter.n_objects < object_num:
                        prefix_counter.n_objects = object_num + 1
                        prefix_counter.save()
                    returning.append(
                        db_utils().messages(
                            parameters={"object_id": constructed_obj_id}
                        )["201_create"]
                    )
                else:
                    object_num = format(prefix_counter.n_objects, "06d")
                    version = publish_object["contents"]["provenance_domain"]["version"]
                    constructed_obj_id = (
                        root_uri + "/" + prefix + "_" + object_num + "/" + version
                    )

                    new_object = {}
                    new_object["contents"] = publish_object["contents"]
                    new_object["object_id"] = constructed_obj_id
                    new_object["contents"]["object_id"] = constructed_obj_id
                    new_object["owner_group"] = publish_object["owner_group"]
                    new_object["owner_user"] = user.username
                    new_object["prefix"] = prefix
                    new_object["last_update"] = timezone.now()
                    new_object["schema"] = "IEEE"
                    new_object["state"] = "PUBLISHED"

                    objects_written = db_utils().write_object(
                        p_app_label="api",
                        p_model_name="BCO",
                        p_fields=[
                            "contents",
                            "last_update",
                            "object_id",
                            "owner_group",
                            "owner_user",
                            "prefix",
                            "schema",
                            "state",
                        ],
                        p_data=new_object,
                    )

                    prefix_counter.n_objects = prefix_counter.n_objects + 1
                    prefix_counter.save()
                    returning.append(
                        db_utils().messages(
                            parameters={"object_id": constructed_obj_id}
                        )["201_create"]
                    )

            else:
                returning.append(
                    db_utils().messages(parameters={"prefix": prefix})[
                        "401_prefix_unauthorized"
                    ]
                )
                any_failed = True

        else:
            returning.append(
                db_utils().messages(parameters={"prefix": prefix})["404_missing_prefix"]
            )
            any_failed = True

    if any_failed:
        return Response(status=status.HTTP_207_MULTI_STATUS, data=returning)

    return Response(status=status.HTTP_200_OK, data=returning)
