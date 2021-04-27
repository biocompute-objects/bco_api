# Explanation of optional fields:  https://stackoverflow.com/questions/16349545/optional-fields-in-django-models
# TextField is used here because it has no character limit.

# Create a base model, then inherit for each table.
# See the 4th example under "Model Inheritance" at https://docs.djangoproject.com/en/3.1/topics/db/models/#model-inheritance

from django.db import models

from django.conf import settings

# For reading the configuration file.
from api.scripts import DbUtils

# --- Permissions imports --- #

# Linking API keys to users.
# Source: https://florimondmanca.github.io/djangorestframework-api-key/guide/#api-key-models
from rest_framework_api_key.models import AbstractAPIKey

# Source: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html

# The user model is straight from Django.
from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver

# For token creation.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
from rest_framework.authtoken.models import Token

# Issue with timezones.
# Source: https://stackoverflow.com/a/32411560
from django.utils import timezone


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


# Link prefixes to groups
class prefix_groups(models.Model):

	# Each prefix has exactly one group owner.

	# The choices of group are taken directly from the table.

	prefix = models.CharField(max_length = 5)

	group_owner = models.CharField(max_length = 1000)


# For registering new users.
class new_users(models.Model):

	# Instead of using the User model, just use
	# a crude table to store the temporary information
	# when someone asks for a new account.

	email = models.EmailField()

	# TODO: hash field in future?
	temp_identifier = models.TextField(max_length = 100)

	# Issue with time zone, so implement the fix.
	# Source: https://stackoverflow.com/a/32411560
	created = models.DateTimeField(default = timezone.now)


# Link prefixes to tables
# class prefix_tables(models.Model):

# 	# Each prefix can only be tied to one table,
# 	# but multiple prefixes can be tied to one table.

# 	table = models.CharField(max_length = 1000)

# 	prefixes = models.JSONField()


# TODO: put all of this under a flag later so that cloning
# GitHub does not automatically erase the database...

# Create referrable dict.
models_dict = {}

# Go through each template and create the associated table.
for template, tables in settings.TABLES.items():

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



# --- Permissions models --- #


# User and API Information is kept separate so that we can use it
# elsewhere easily.

# Source: https://florimondmanca.github.io/djangorestframework-api-key/guide/#api-key-models
# Source: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html




# If we want a separate API users table.
# # All users for the API.
# class api_users(models.Model):
	
# 	user = models.OneToOneField(User, on_delete = models.CASCADE)
# 	group = models.ForeignKey(Group, on_delete = models.CASCADE)

# 	# Display the username properly in the admin.
# 	# Source: https://stackoverflow.com/a/61991068/5029459	
# 	def __str__(self):
# 		return self.user.username

# Link user creation to groups.
@receiver(post_save, sender = User)
def associate_user_group(sender, instance, created, **kwargs):
	
	if created:
		
		# Create a group for this user.
		# Source: https://stackoverflow.com/a/55206382/5029459
		Group.objects.create(name = instance)
		group = Group.objects.get(name = instance)
		group.user_set.add(instance)

# Link user creation to token generation.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens

# TODO: user settings.AUTH_USER_MODEL?

@receiver(post_save, sender = User)
def create_auth_token(sender, instance=None, created=False, **kwargs):

	if created:
		Token.objects.create(user=instance)


# If we want a separate API users table.
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
# 	instance.User.save()


# Link API keys to users.
class api_users_api_key(AbstractAPIKey):
	
	user = models.ForeignKey(
		User,
		on_delete = models.CASCADE,
		related_name = 'api_keys'
	)
