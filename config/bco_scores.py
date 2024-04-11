#!/usr/bin/env python3

import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bcodb.settings")
django.setup()

from django.db.models import F
from django.db.models.functions import Length
from biocompute.models import BCO

def main():
    """
    Process and score BioCompute Objects (BCOs) based on the length of their usability_domain.

    This function performs the following steps:
    1. Fetches all published BCOs from the database, specifically retrieving their object_id and 
       the contents of their usability_domain.
    2. Calculates a 'score' for each BCO, which is the sum of the lengths of strings within the 
       usability_domain field. If the usability_domain is not present or is invalid, a score of 0 is assigned.
    3. Sorts the BCOs in descending order based on their scores.
    4. Outputs the sorted list of BCOs, along with their scores, to a JSON file named 'bco_scores.json'.

    The scoring and sorting help in identifying BCOs with more detailed and potentially more useful usability domains.
    """
    # Fetching all BCOs with their id and usability_domain
    bcos = BCO.objects.filter(state='PUBLISHED').annotate(
        usability_domain=F('contents__usability_domain')
        ).values('object_id', 'usability_domain')

    bcos_list = list(bcos)

    count = 0
    for bco in bcos_list:

        try:
            usability_domain_length = sum(len(s) for s in bco['usability_domain'])
            count += 1
            bco['score'] = {
                "usability_domain_length": usability_domain_length
            }
        except TypeError:
            import pdb; pdb.set_trace()
            bco['score'] = {
                "usability_domain_length": 0
            }
            count += 1

    sorted_list_of_dicts = sorted(bcos_list, key=lambda d: d['score']['usability_domain_length'], reverse=True)

    with open('bco_scores.json', "w") as file:
        json.dump(sorted_list_of_dicts, file, indent=4)

if __name__ == "__main__":
    main()