from rest_framework import serializers
from .models import bco_draft, bco_publish


# ----- Request Serializers ----- #

# Serializers must be abstracted in order to use abstracted models.
# Source (last solution): https://stackoverflow.com/questions/33137165/django-rest-framework-abstract-class-serializer

# Base serializers to be inherited by each model.
class TypeBaseSerializer(serializers.Serializer):
    
    # Arguments
    # incoming_table: the table to write to.

    # Set the model.
    exec('model = ' + self.context.get(incoming_table))

    # Need to re-declare fields since this is not a ModelSerializer.

    # Have to use CharField instead of TextField, see https://stackoverflow.com/questions/38849201/how-to-serialize-bigintegerfield-textfield-in-serializer-django
    object_id = serializers.CharField()
    schema = serializers.CharField()
    contents = serializers.JSONField()
    object_class = serializers.CharField()
    state = serializers.CharField()

    class Meta:
        fields = ['object_id', 'schema', 'contents', 'state']


class GenericObjectSerializer(TypeBaseSerializer, serializers.ModelSerializer):

    class Meta:
        fields = TypeBaseSerializer.Meta.fields

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