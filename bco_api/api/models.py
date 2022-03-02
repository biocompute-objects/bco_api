"""
Explanation of optional fields:  https://stackoverflow.com/questions/16349545/optional-fields-in-django-models
TextField is used here because it has no character limit.

Create a base model, then inherit for each table.
See the 4th example under "Model Inheritance" at https://docs.djangoproject.com/en/3.1/topics/db/models/#model-inheritance
"""

from django.db import models
# Source: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
# For setting the anonymous key.
from django.conf import settings
# The user model is straight from Django. (BAD WAY TO DO THIS) Should be: 
#   from django.contrib.auth import get_user_model
#   User = get_user_model()

from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
import django.db.utils as PermErrors
# Referencing models.
from django.contrib.contenttypes.models import ContentType
# Issue with timezones.
# Source: https://stackoverflow.com/a/32411560
from django.utils import timezone
# Object-level permissions.
from guardian.shortcuts import assign_perm
# For token creation.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
from rest_framework.authtoken.models import Token

class Prefix(models.Model):
    """BioCompute Prefix Model.

     ...

    Attributes
    ----------
    prefix: str
        Prefix and primary key for this class
    certifying_server: TextField, optional
        Indicates server this prefix certified by.
    certifying_key: TextField, optional
        certifying key.
    created: DateTimeField, optional
        When was prefix created
    created_by: User.username
        User who created this prefix
    description: str, optional
        Descriptive string for this prefix
    expires: DateTimeField, optional
        Date and time indicating if the prefix expires
    owner_group: Group.name,
        Group that owns this prefix. Each prefix has exactly one group owner.
    owner_user: User.username
        User that owns this prefix. Each prefix has exactly one user owner.

    Methods
    -------
    __str__(self)
        String for representing the model (in Admin site etc.)
    """

    prefix = models.CharField(max_length=5, unique=True, primary_key=True)
    certifying_server = models.TextField(blank = True, null = True)
    certifying_key = models.TextField(blank = True,  null = True)
    created = models.DateTimeField(default = timezone.now, blank = True, null = True)
    created_by = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'created_by',
        to_field = 'username',
        default='wheel')
    description = models.TextField(blank = True, null = True)
    expires = models.DateTimeField(blank = True, null = True)
    n_objects = models.IntegerField(default=1)
    owner_group = models.ForeignKey(Group, on_delete=models.CASCADE, to_field='name')
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username')

    def __str__(self):
        """
        String for representing the BCO model (in Admin site etc.).
        """
        return str(self.prefix)

# Generic BCO model
class BCO(models.Model):
    """
    Class used to represent BioCompute Objects(BCO).

    Attributes
    ----------
    object_id: str
        BCO id for this class
    contents: str, JSON
        Raw JSON contents of BCO
    object_class: str, optional
        Used to describe overall purpose of the object.
    owner_group: ForeignKey
        The object owner group.
    owner_user: ForeignKey
        The object owner group
    prefix: ForeignKey
        prefix the object falls under
    schema: str
        Schema defining object
    state: str
        The state of the object, is it a draft, embargoed, or published
    last_update: DateTimeField
        When the draft was last updated

    Methods
    -------
    __str__(self)
        String for representing the model (in Admin site etc.)
    """

    id = models.AutoField(primary_key=True)
    object_id = models.TextField()
    contents = models.JSONField()
    # TODO Embargo field.
    object_class = models.TextField(blank=True, null=True)
    owner_group = models.ForeignKey(Group, on_delete=models.SET_NULL, to_field='name', null=True)
    owner_user = models.ForeignKey(User, on_delete=models.SET_NULL, to_field='username', null=True)
    prefix = models.ForeignKey(Prefix, to_field='prefix', on_delete=models.PROTECT)
    schema = models.TextField()
    state = models.TextField()
    last_update = models.DateTimeField()

    def __str__(self):
        """String for representing the BCO model (in Admin site etc.)."""
        return str(self.object_id)

class GroupInfo(models.Model):
    """
    Some additional information for Group.
    This information is stored separately from
    Group so as to not complicate or compromise
    anything relating to authentication.
    Delete group members on group deletion?
    """
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        to_field='name',
        primary_key=True
    )
    delete_members_on_group_deletion = models.BooleanField(default=False)
    description = models.TextField(blank = True)
    expiration = models.DateTimeField(blank=True, null=True)
    max_n_members = models.IntegerField(blank=True, null=True)
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username')

# For registering new users.
class NewUsers(models.Model):
    """
    Instead of using the User model, just use
    a crude table to store the temporary information
    when someone asks for a new account.
    In case we are writing back to UserDB.
    Which host to send the activation back to (i.e. UserDB).
    Issue with time zone, so implement the fix.
    Source: https://stackoverflow.com/a/32411560
    """

    email = models.EmailField(primary_key=True)
    temp_identifier = models.TextField(max_length=100)
    token = models.TextField(blank=True, null=True)
    hostname = models.TextField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)

# def get_first_name(self):
#     return self.first_name

# User.add_to_class("__str__", get_first_name)


# --- Receivers --- #


# User and API Information are kept separate so that we can use it
# elsewhere easily.

# Source: https://florimondmanca.github.io/djangorestframework-api-key/guide/#api-key-models
# Source: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html


# --- User --- #


# Link user creation to groups.
@receiver(post_save, sender=User)
def associate_user_group(sender, instance, created, **kwargs):
    """
    Create a group for this user.
    Source: https://stackoverflow.com/a/55206382/5029459
    Automatically add the user to the BCO drafters and publishers groups,
    if the user isn't anon or the already existent bco_drafter or bco_publisher.
    """

    if created:
        try:
            Group.objects.get(name=instance)
        except Group.DoesNotExist:
            Group.objects.create(name=instance)
        group = Group.objects.get(name=instance)
        group.user_set.add(instance)

        if instance.username not in ['anon', 'bco_drafter', 'bco_publisher']:
            User.objects.get(username=instance).groups.add(Group.objects.get(name='bco_drafter'))
            User.objects.get(username=instance).groups.add(Group.objects.get(name='bco_publisher'))

# Link user creation to token generation.
# Source: https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
@receiver(
    post_save,
    sender=User
)
def create_auth_token(
        sender,
        instance=None,
        created=False,
        **kwargs
):
    if created:

        # The anonymous user's token is hard-coded
        # in server.conf.
        if instance.username == 'anon':

            # Create anon's record with the hard-coded key.
            Token.objects.create(
                user=instance,
                key=settings.ANON_KEY
            )

        else:

            # Create a normal user's record.
            Token.objects.create(
                user=instance
            )


# --- Group --- #


# Link group deletion to permissions deletion.

# pre_delete and NOT post_delete because we need
# to get the Group's information before deleting it.
@receiver(
    pre_delete,
    sender=Group
)
def delete_group_perms(
        sender,
        instance=None,
        **kwargs
):
    for perm in ['add_members_' + instance.name, 'delete_members_' + instance.name]:
        Permission.objects.filter(
            codename=perm
        ).delete()


# --- Prefix --- #


# Link prefix creation to permissions creation.
@receiver(post_save, sender=Prefix)
def create_permissions_for_prefix(sender, instance=None, created=False, **kwargs):
    """
    Test
    """

    if created:
        # Check to see whether or not the permissions
        # have already been created for this prefix.
        try:
            # Create the macro-level, draft, and publish permissions.
            for perm in ['add', 'change', 'delete', 'view', 'draft', 'publish']:
                Permission.objects.create(
                    name='Can ' + perm + ' BCOs with prefix ' + instance.prefix,
                    content_type=ContentType.objects.get(app_label='api', model='bco'),
                    codename=perm + '_' + instance.prefix
                )

                # Give FULL permissions to the prefix user owner
                # and their group.
                owner_user = User.objects.get(username=instance.owner_user)
                for permission in Permission.objects.filter(codename=perm + '_' + instance.prefix):
                    owner_user.user_permissions.add(permission)
                owner_group = Group.objects.get(name=instance.owner_user)
                for permission in Permission.objects.filter(codename=perm + '_' + instance.prefix):
                    owner_group.permissions.add(permission)
 
        except PermErrors.IntegrityError:

            # The permissions already exist.
            pass

@receiver(post_delete, sender=Prefix)
def delete_permissions_for_prefix(sender, instance=None, **kwargs):
    """
    Link prefix deletion to permissions deletion.
    No risk of raising an error when using
    a filter.
    """

    Permission.objects.filter(codename='add_' + instance.prefix).delete()
    Permission.objects.filter(codename='change_' + instance.prefix).delete()
    Permission.objects.filter(codename='delete_' + instance.prefix).delete()
    Permission.objects.filter(codename='view_' + instance.prefix).delete()
    Permission.objects.filter(codename='draft_' + instance.prefix).delete()
    Permission.objects.filter(codename='publish_' + instance.prefix).delete()

@receiver(post_save, sender=GroupInfo)
def create_group_perms(sender, instance=None, created=False, **kwargs):
    """
    Link group creation to permission creation.
    Check to see whether or not the permissions
    have already been created for this prefix.

    Create the permissions, then use group_info to give the group admin
    the admin permissions.
    Create the administrative permissions for the group.
    Give the administrative permissions to the user
    creating this group.
    """
    if created:
        try:
            for perm in ['add_members_' + Group.objects.get(name=instance.group_id).name,
                         'delete_members_' + Group.objects.get(name=instance.group_id).name]:
                Permission.objects.create(
                    name='Can ' + perm,
                    content_type=ContentType.objects.get(app_label='auth', model='group'),
                    codename=perm)
                User.objects.get(username=instance.owner_user_id).user_permissions.add(Permission.objects.get(codename=perm))

        except PermErrors.IntegrityError:

            # The permissions already exist.
            pass


# --- BCO --- #


# Link draft creation to permission creation
@receiver(
    post_save,
    sender=BCO
)
def create_object_perms(
        sender,
        instance=None,
        created=False,
        **kwargs
):
    if created:

        # Check to see whether or not the permissions
        # have already been created for this object.
        try:

            # Only do anything if the save was for a
            # draft object.
            if instance.state == 'DRAFT':

                # The owner group can only initially view
                # the object.
                for p in ['change_' + instance.object_id, 'delete_' + instance.object_id,
                          'publish_' + instance.object_id, 'view_' + instance.object_id]:

                    Permission.objects.create(
                        name='Can ' + p,
                        content_type=ContentType.objects.get(
                            app_label='api',
                            model='bco'
                        ),
                        codename=p
                    )

                    # Give wheel everything.
                    assign_perm(
                        perm=Permission.objects.get(codename=p),
                        user_or_group=User.objects.get(username='wheel'),
                        obj=instance
                    )

                    # Create the permission, and automatically give it
                    # to the owner group, NOT the owner user (owner user
                    # is checked for directly in requests and thus
                    # there is no need for assigning the permission
                    # to the user).

                    # The owner group can only initially view
                    # the object.

                    # guardian can't take a string name here for
                    # some reason...
                    if p == 'view_' + instance.object_id:
                        assign_perm(
                            perm=Permission.objects.get(codename=p),
                            user_or_group=Group.objects.get(name=instance.owner_group),
                            obj=instance
                        )

            elif instance.state == 'PUBLISHED':

                # Create the publish permission, which allows others
                # use the object ID to make new versions of the published
                # object.
                Permission.objects.create(
                    name='Can publish a new version of an existing published object',
                    content_type=ContentType.objects.get(
                        app_label='api',
                        model='bco'
                    ),
                    codename='publish_new_version_' + instance.object_id
                )

                # Only the object owner has default permissions to publish
                # subsequent versions...

                # Give wheel everything.
                assign_perm(
                    perm=Permission.objects.get(codename='publish_new_version_' + instance.object_id),
                    user_or_group=User.objects.get(username='wheel'),
                    obj=instance
                )

        except PermErrors.IntegrityError:

            # The permissions already exist.
            pass


# Link object deletion to object permissions deletion.

# TODO:...
