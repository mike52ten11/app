# Generated by Django 4.2.8 on 2024-01-26 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writedata', '0008_rename_user_device'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceTransfor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('QRid', models.CharField(max_length=100)),
                ('deviceUuid', models.CharField(max_length=100)),
            ],
        ),
    ]
