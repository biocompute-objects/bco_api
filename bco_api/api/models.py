# Explanation of optional fields:  https://stackoverflow.com/questions/16349545/optional-fields-in-django-models
# TextField is used here because it has no character limit.

# Create a base model, then inherit for each table.
# See the 4th example under "Model Inheritance" at https://docs.djangoproject.com/en/3.1/topics/db/models/#model-inheritance

from django.db import models

# For reading the configuration file.
from django.conf import settings




# --- Permissions imports --- #




# Source: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html

# The user model is straight from Django.
from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Issue with timezones.
# Source: https://stackoverflow.com/a/32411560
from django.utils import timezone

# For token creation.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
from rest_framework.authtoken.models import Token




# Ownership models
# Source: https://stackoverflow.com/a/47268403
class owned_model(
	models.Model
):


	# The object owner (should be a group).
	owner_group = models.ForeignKey(
		Group, 
		on_delete = models.CASCADE
	)


	class Meta:
		abstract = True


# Generic JSON model
class json_object(
	owned_model
):


	# The entirety of the object.

	# Field is required.
	contents = models.JSONField()

	
	# The unique object ID.

	# Field is required.
	object_id = models.TextField()


	# The schema under which the object falls.

	# Field is required.
	schema = models.TextField()


	# The state of the object, is it a draft or is it published?

	# Field is required.
	state = models.TextField()


	# What is the class of the object (typically used to describe overall
	# purpose of the object)?

	# Field is optional.
	object_class = models.TextField(
		blank = True, 
		null = True
	)


	# Make this class a parent.
	class Meta:
		abstract = True


# Generic meta data model
class meta_table(
	models.Model
):


	# The number of objects in a given table.

	# Field is required.
	n_objects = models.IntegerField()


	# Make this class a parent.
	class Meta:
		abstract = True


# Link prefixes to groups
class prefix_groups(
	models.Model
):

	# Each prefix has exactly one group owner.

	# The choices of group are taken directly from the table.

	group_owner = models.CharField(
		max_length = 1000
	)
	
	prefix = models.CharField(
		max_length = 5
	)


# For registering new users.
class new_users(
	models.Model
):

	# Instead of using the User model, just use
	# a crude table to store the temporary information
	# when someone asks for a new account.

	email = models.EmailField()
	
	temp_identifier = models.TextField(
		max_length = 100
	)

	# In case we are writing back to user db.
	token = models.TextField(
		blank = True, 
		null = True
	)

	# Which host to send the activation back to.
	hostname = models.TextField(
		blank = True, 
		null = True
	)

	# Issue with time zone, so implement the fix.
	# Source: https://stackoverflow.com/a/32411560
	created = models.DateTimeField(
		default = timezone.now
	)

# Create referrable dict.
models_dict = {}

# Go through each template and create the associated table.
for template, tables in settings.TABLES.items():

	# lower because the model names are lowercase.
	lowered = template.lower()

	# Register the template with the "global" dict.
	models_dict[
		lowered
	] = []

	for table in tables:

		# Replace later with model registration...
		exec('class ' + table + '(' + lowered + '):\n\tpass')

		# Register the table with the "global" variable.
		models_dict[
			lowered
		].append(
			table
		)

# Now define the global variable (is this actually used anywhere?
# some places are using app_info...).
settings.MODELS = models_dict




# --- Permissions receivers --- #




# User and API Information is kept separate so that we can use it
# elsewhere easily.

# Source: https://florimondmanca.github.io/djangorestframework-api-key/guide/#api-key-models
# Source: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html

# Link user creation to groups.
@receiver(
	post_save, 
	sender = User
)
def associate_user_group(
	sender, 
	instance, 
	created, 
	**kwargs
):
	
	if created:
		
		# Create a group for this user.
		# Source: https://stackoverflow.com/a/55206382/5029459
		Group.objects.create(
			name = instance
		)
		group = Group.objects.get(
			name = instance
		)
		group.user_set.add(
			instance
		)

		# Automatically add BCO draft and BCO publish permissions.

		# anon does NOT have drafter or publisher permissions.
		if instance.username != 'anon':
			User.objects.get(
				username = instance
			).groups.add(
				Group.objects.get(
					name = 'bco_drafters'
				)
			)
			User.objects.get(
				username = instance
			).groups.add(
				Group.objects.get(
					name = 'bco_publishers'
				)
			)


# Link user creation to token generation.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens

@receiver(
	post_save, 
	sender = User
)
def create_auth_token(
	sender, 
	instance = None, 
	created = False, 
	**kwargs
):

	if created:
		Token.objects.create(
			user = instance
		)