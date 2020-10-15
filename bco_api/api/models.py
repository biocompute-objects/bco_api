from django.db import models

# Create your models here.

# Explanation of optional fields:  https://stackoverflow.com/questions/16349545/optional-fields-in-django-models
# TextField is used here because it has no character limit.

# Create a base model, then inherit for each table.
# See the 4th example under "Model Inheritance" at https://docs.djangoproject.com/en/3.1/topics/db/models/#model-inheritance


# Generic BCO model
class bco_object(models.Model):


	# The unique object ID.

	# Field is required.
	object_id = models.TextField()


	# The schema under which the object falls.

	# Field is optional.
	schema = models.TextField(blank=True, null=True)


	# The entirety of the BCO.

	# Field is optional.
	bco = models.TextField(blank=True, null=True)


	# What is the class of the object (typically used to describe overall
	# purpose of the object)?

	# Field is optional.
	object_class = models.TextField(blank=True, null=True)


	# The state of the object, is it a draft or is it committed?

	# Field is optional.
	state = models.TextField(blank=True, null=True)


	# Make this class a parent.
	class Meta:
		abstract = True


# Galaxy table
class galaxy(bco_object):
	pass


# GlyGen table
class glygen(bco_object):
	pass


# OncoMX table
class oncomx(bco_object):
	pass
