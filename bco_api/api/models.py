# Explanation of optional fields:  https://stackoverflow.com/questions/16349545/optional-fields-in-django-models
# TextField is used here because it has no character limit.

# Create a base model, then inherit for each table.
# See the 4th example under "Model Inheritance" at https://docs.djangoproject.com/en/3.1/topics/db/models/#model-inheritance

from django.db import models




# --- Permissions imports --- #




# Source: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html

# The user model is straight from Django.
from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import django.db.utils as PermErrors

# Referencing models.
from django.contrib.contenttypes.models import ContentType

# Issue with timezones.
# Source: https://stackoverflow.com/a/32411560
from django.utils import timezone

# For token creation.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
from rest_framework.authtoken.models import Token


# Generic BCO model
class bco(
	models.Model
):


	# The entirety of the object.

	# Field is required.
	contents = models.JSONField()


	# What is the class of the object (typically used to describe overall
	# purpose of the object)?

	# Field is optional.
	object_class = models.TextField(
		blank = True, 
		null = True
	)


	# The unique object ID.

	# Field is required.
	object_id = models.TextField()


	# The object owner (should be a group).
	owner_group = models.ForeignKey(
		Group, 
		on_delete = models.CASCADE
	)

	# The object owner (should be a user).
	owner_user = models.ForeignKey(
		User,
		on_delete = models.CASCADE
	)


	# Which prefix the object falls under.

	# Field is required.
	prefix = models.CharField(
		max_length = 5
	)
	
	
	# The schema under which the object falls.

	# Field is required.
	schema = models.TextField()


	# The state of the object, is it a draft, embargoed, or published?

	# Field is required.
	state = models.TextField()


# Generic meta data model
class meta_table(
	models.Model
):


	# The number of objects for a given prefix.

	# Field is required.
	n_objects = models.IntegerField()


	# Which prefix the object falls under.

	# Field is required.
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


# Link prefixes to groups
class prefixes(
	models.Model
):


	# Each prefix has exactly one group owner.
	owner_group = models.ForeignKey(
		Group, 
		on_delete = models.CASCADE
	)

	# Each prefix has exactly one user owner.
	owner_user = models.ForeignKey(
		User, 
		on_delete = models.CASCADE
	)
	
	prefix = models.CharField(
		max_length = 5
	)




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

		# Automatically add the user to the BCO drafters and publishers groups,
		# if the user isn't anon or the already existent bco_drafter or bco_publisher.
		if instance.username not in ['anon', 'bco_drafter', 'bco_publisher']:
			
			User.objects.get(
				username = instance
			).groups.add(
				Group.objects.get(
					name = 'bco_drafter'
				)
			)
			User.objects.get(
				username = instance
			).groups.add(
				Group.objects.get(
					name = 'bco_publisher'
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


# Link prefix creation to permissions creation.

@receiver(
	post_save,
	sender = prefixes
)
def create_permissions_for_prefix(
	sender,
	instance = None,
	created = False,
	**kwargs
):

	if created:
		
		# Check to see whether or not the permissions
		# have already been created for this prefix.
		try:

			for perm in ['add', 'change', 'delete', 'view']:
			
				Permission.objects.create(
					name = 'Can ' + perm + ' BCOs with prefix ' + instance.prefix,
					content_type = ContentType.objects.get(
						app_label = 'api',
						model = 'bco'
					),
					codename = perm + '_' + instance.prefix
				)

				# Give FULL permissions to the prefix user owner
				# and their group.

				# No try/except necessary here as the user's existence
				# has already been verified upstream.

				# Source: https://stackoverflow.com/a/20361273
				
				User.objects.get(
					username = instance.owner_user
				).user_permissions.add(
					Permission.objects.get(
						codename = perm + '_' + instance.prefix
					)
				)
				
				Group.objects.get(
					name = instance.owner_user
				).permissions.add(
					Permission.objects.get(
						codename = perm + '_' + instance.prefix
					)
				)
		
		except PermErrors.IntegrityError:
			
			# The permissions already exist.			
			pass


# Link prefix deletion to permissions deletion.

@receiver(
	post_delete,
	sender = prefixes
)
def delete_permissions_for_prefix(
	sender,
	instance = None,
	**kwargs
):
		
	# No risk of raising an error when using
	# a filter.
	Permission.objects.filter(
		codename = 'add_' + instance.prefix
	).delete()

	Permission.objects.filter(
		codename = 'change_' + instance.prefix
	).delete()

	Permission.objects.filter(
		codename = 'delete_' + instance.prefix
	).delete()

	Permission.objects.filter(
		codename = 'view_' + instance.prefix
	).delete()