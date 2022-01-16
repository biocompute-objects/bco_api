# Generated by Django 3.2.4 on 2021-12-28 17:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0002_auto_20211221_2309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group_info',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group', to_field='name'),
        ),
        migrations.AlterField(
            model_name='group_info',
            name='owner_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username'),
        ),
    ]
