# Generated by Django 4.2.6 on 2023-12-25 06:48

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("writedata", "0007_user_delete_userprofile"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="USER",
            new_name="Device",
        ),
    ]