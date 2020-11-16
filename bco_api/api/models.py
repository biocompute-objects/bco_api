from django.db import models

# Create your models here.

# Explanation of optional fields:  https://stackoverflow.com/questions/16349545/optional-fields-in-django-models
# TextField is used here because it has no character limit.

# Create a base model, then inherit for each table.
# See the 4th example under "Model Inheritance" at https://docs.djangoproject.com/en/3.1/topics/db/models/#model-inheritance


# Generic BCO model
class json_object(models.Model):


	# The unique object ID.

	# Field is required.
	object_id = models.TextField()


	# The schema under which the object falls.

	# Field is required.
	schema = models.TextField()


	# The entirety of the object.

	# Field is required.
	contents = models.TextField()


	# What is the class of the object (typically used to describe overall
	# purpose of the object)?

	# Field is optional.
	object_class = models.TextField(blank=True, null=True)


	# The state of the object, is it a draft or is it published?

	# Field is required.
	state = models.TextField()


	# Make this class a parent.
	class Meta:
		abstract = True


# BCO tables
class bco_draft(json_object):
	pass

class bco_publish(json_object):
	pass


# Galaxy tables
class galaxy_draft(json_object):
	pass

class galaxy_publish(json_object):
	pass


# GlyGen tables
class glygen_draft(json_object):
	pass

class glygen_publish(json_object):
	pass


# OncoMX tables
class oncomx_draft(json_object):
	pass

class oncomx_publish(json_object):
	pass
