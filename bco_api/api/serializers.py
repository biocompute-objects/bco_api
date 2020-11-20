from rest_framework import serializers
from .models import bco_draft, bco_publish


# ----- Request Serializers ----- #

# Serializers must be abstracted in order to use abstracted models.
# Source (last solution): https://stackoverflow.com/questions/33137165/django-rest-framework-abstract-class-serializer

# Base serializers to be inherited by each model.

# Abstract so that any model can be used.

# Source (4th response): https://stackoverflow.com/questions/30831731/create-a-generic-serializer-with-a-dynamic-model-in-meta

def getGenericSerializer(incoming_model):

    class GenericObjectSerializer(serializers.ModelSerializer):
    
    # Arguments
    # incoming_table: the table to write to.

    # Need to re-declare fields since this is not a ModelSerializer.

    # Have to use CharField instead of TextField, see https://stackoverflow.com/questions/38849201/how-to-serialize-bigintegerfield-textfield-in-serializer-django
    #object_id = serializers.CharField()
    #schema = serializers.CharField()
    #contents = serializers.JSONField()
    #object_class = serializers.CharField()
    #state = serializers.CharField()

        class Meta:
            model = incoming_model
            fields = ['object_id', 'schema', 'contents', 'state']

    return GenericObjectSerializer

'''
# Model-based serializer for POST.
class JsonPostSerializer(TypeBaseSerializer, serializers.ModelSerializer):

    # Required to be able to pass JSON in the POST.
    # Source:  https://stackoverflow.com/questions/50374192/not-a-valid-string-error-when-trying-save-dict-to-textfield-in-django-rest
    #bco = serializers.JSONField()

    class Meta:
        model = json_object
        #fields = TypeBaseSerializer.Meta.fields + ['schema', 'bco', 'object_class', 'state']
        #fields = ['object_id', 'schema', 'bco', 'object_class', 'state']


# Model based serializer for GET.
class JsonGetSerializer(TypeBaseSerializer):
    
    # Required to be able to pass JSON in the POST.
    # Source:  https://stackoverflow.com/questions/50374192/not-a-valid-string-error-when-trying-save-dict-to-textfield-in-django-rest
    generic_serializer = serializers.JSONField()

    class Meta:
        model = json_object
        fields = ['object_id']


# Model based serializer for PATCH.
class JsonPatchSerializer(serializers.Serializer):
    class Meta:
        model = json_object
        fields = ['object_id']


# Model-based serializer for DELETE.
class JsonDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = json_object
        fields = ['object_id']


# ----- Other Serializers ----- #


# Serializer for retrieving objects from the database.
'''