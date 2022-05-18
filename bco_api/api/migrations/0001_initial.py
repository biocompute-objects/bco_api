# Generated by Django 3.2.10 on 2022-05-18 19:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='new_users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('temp_identifier', models.TextField(max_length=100)),
                ('token', models.TextField(blank=True, null=True)),
                ('hostname', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='prefix_table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_objects', models.IntegerField()),
                ('prefix', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Prefix',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certifying_server', models.TextField(blank=True, null=True)),
                ('certifying_key', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('expires', models.DateTimeField(blank=True, null=True)),
                ('prefix', models.CharField(max_length=5)),
                ('created_by', models.ForeignKey(default='wheel', on_delete=django.db.models.deletion.CASCADE, related_name='created_by', to=settings.AUTH_USER_MODEL, to_field='username')),
                ('owner_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group', to_field='name')),
                ('owner_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
        migrations.CreateModel(
            name='GroupInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delete_members_on_group_deletion', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True)),
                ('expiration', models.DateTimeField(blank=True, null=True)),
                ('max_n_members', models.IntegerField(blank=True, null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group', to_field='name')),
                ('owner_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
        migrations.CreateModel(
            name='BCO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contents', models.JSONField()),
                ('object_class', models.TextField(blank=True, null=True)),
                ('object_id', models.TextField()),
                ('prefix', models.CharField(max_length=5)),
                ('schema', models.TextField()),
                ('state', models.TextField()),
                ('last_update', models.DateTimeField()),
                ('owner_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group', to_field='name')),
                ('owner_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
    ]
