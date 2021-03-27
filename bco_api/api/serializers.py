from rest_framework import serializers
#from .models import bco_draft, bco_publish

# --- Permissions imports --- #

from django.contrib.auth.models import User

# Groups require special processing.
# Source: https://stackoverflow.com/questions/33844003/how-to-serialize-groups-of-a-user-with-django-rest-framework/33844179
from django.contrib.auth.models import Group

# Keys model
from .models import ApiInfo




# ----- Request Serializers ----- #

# Serializers must be abstracted in order to use abstracted models.
# Source (last solution): https://stackoverflow.com/questions/33137165/django-rest-framework-abstract-class-serializer

# Base serializers to be inherited by each model.

# Abstract so that any model can be used.

# Source (4th response): https://stackoverflow.com/questions/30831731/create-a-generic-serializer-with-a-dynamic-model-in-meta

def getGenericSerializer(incoming_model, incoming_fields):

    class GenericObjectSerializer(serializers.ModelSerializer):
    
    # Arguments
    # incoming_table: the table to write to.

        class Meta:
            model = incoming_model
            fields = incoming_fields

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




# API serializer
class ApiSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApiInfo
        fields = ('hostname', 'human_readable', 'apikey',)


class GroupSerializer(serializers.ModelSerializer):    
    
    class Meta:
        model = Group
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):

    apiinfo = ApiSerializer(source='custom_user', many=True)
    groups = GroupSerializer(many=True)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email', 'groups', 'apiinfo',)