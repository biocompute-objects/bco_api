from rest_framework import serializers
from .models import bco_object


# ----- Request Serializers ----- #

# Serializers must be abstracted in order to use abstracted models.
# Source: https://stackoverflow.com/questions/33137165/django-rest-framework-abstract-class-serializer

# Base serializers to be inherited by each request method.
class TypeBaseSerializer(serializers.Serializer):
    class Meta:
        fields = ['object_id']
        abstract = True

# Model-based serializer for POST.
class BcoPostSerializer(TypeBaseSerializer):

    # Required to be able to pass JSON in the POST.
    # Source:  https://stackoverflow.com/questions/50374192/not-a-valid-string-error-when-trying-save-dict-to-textfield-in-django-rest
    bco = serializers.JSONField()

    class Meta:
        model = bco_object
        fields = TypeBaseSerializer.Meta.fields + ['schema', 'bco', 'object_class', 'state']
        #fields = ['object_id', 'schema', 'bco', 'object_class', 'state']


# Model based serializer for GET.
class BcoGetSerializer(serializers.Serializer):
    class Meta:
        model = bco_object
        fields = ['object_id']


# Model based serializer for PATCH.
class BcoPatchSerializer(serializers.Serializer):
    class Meta:
        model = bco_object
        fields = ['object_id']


# Model-based serializer for DELETE.
class BcoDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = bco_object
        fields = ['object_id']


# ----- Other Serializers ----- #


# Serializer for retrieving objects from the database.