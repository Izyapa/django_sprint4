# Generated by Django 3.2.16 on 2024-02-08 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0020_alter_post_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='comment',
            new_name='post',
        ),
    ]
