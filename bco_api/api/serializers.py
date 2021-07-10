from django.contrib.auth.models import User

# Groups require special processing.
# Source: https://stackoverflow.com/questions/33844003/how-to-serialize-groups-of-a-user-with-django-rest-framework/33844179
from django.contrib.auth.models import Group

from rest_framework import serializers




# ----- Request Serializers ----- #




# Serializers must be abstracted in order to use abstracted models.
# Source (last solution): https://stackoverflow.com/questions/33137165/django-rest-framework-abstract-class-serializer

# Base serializers to be inherited by each model.

# Abstract so that any model can be used.

# Source (4th response): https://stackoverflow.com/questions/30831731/create-a-generic-serializer-with-a-dynamic-model-in-meta

def getGenericSerializer(
    incoming_model, 
    incoming_fields
):

    class GenericObjectSerializer(
        serializers.ModelSerializer
    ):
    
    # Arguments
    # incoming_table: the table to write to.

        class Meta:
            model = incoming_model
            fields = incoming_fields

    return GenericObjectSerializer