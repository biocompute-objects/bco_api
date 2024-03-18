#!/usr/bin/env python3
# prefix/services.py

import re
from urllib.parse import urlparse
from django.conf import settings
from django.utils import timezone
from biocompute.models import Bco
from prefix.models import Prefix
from django.db.models import F

"""Prefix Services

Service functions for working with BCO Prefixes
"""

def prefix_counter_increment(prefix: Prefix) -> int:
    """Prefix Counter Increment 
    
    Simple incrementing function.
    Counter for BCO object_id asignment.
    """
    
    Prefix.objects.update(counter=F("counter") + 1)
    count = prefix.counter
    return count
