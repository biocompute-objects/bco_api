from django.db import models

# Create your models here.

# Explanation of optional fields:  https://stackoverflow.com/questions/16349545/optional-fields-in-django-models
# TextField is used here because it has no character limit.

# Create a base model, then inherit for each table.
# See the 4th example under "Model Inheritance" at https://docs.djangoproject.com/en/3.1/topics/db/models/#model-inheritance

from django.conf import settings
# For reading the configuration file.
from api.scripts import DbUtils


# Generic JSON model
class json_object(models.Model):


	# The unique object ID.

	# Field is required.
	object_id = models.TextField()


	# The schema under which the object falls.

	# Field is required.
	schema = models.TextField()


	# The state of the object, is it a draft or is it published?

	# Field is required.
	state = models.TextField()


	# The entirety of the object.

	# Field is required.
	contents = models.JSONField()


	# What is the class of the object (typically used to describe overall
	# purpose of the object)?

	# Field is optional.
	object_class = models.TextField(blank=True, null=True)


	# Make this class a parent.
	class Meta:
		abstract = True


# Generic meta data model
class meta_table(models.Model):


	# The number of objects in a given table.

	# Field is required.
	n_objects = models.IntegerField()


	# Make this class a parent.
	class Meta:
		abstract = True


# Create referrable dict.
models_dict = {}

# Read the configuration file.
db_settings_from_file = DbUtils.DbUtils().load_settings_file(file_path='./tables.conf')

# Go through each template and create the associated table.
for template, tables in db_settings_from_file.items():

	# lower because the model names are lowercase.
	lowered = template.lower()

	# Register the template with the "global" dict.
	models_dict[lowered] = []

	for table in tables:

		# Replace later with model registration...
		exec('class ' + table + '(' + lowered + '):\n\tpass')

		# Register the table with the "global" variable.
		models_dict[lowered].append(table)

# Now define the global variable (is this actually used anywhere?
# some places are using app_info...).
settings.MODELS = models_dict
