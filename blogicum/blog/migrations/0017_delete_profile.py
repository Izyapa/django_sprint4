# Generated by Django 3.2.16 on 2023-12-19 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_rename_user_profile_username'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
