# Generated by Django 3.2.16 on 2023-12-04 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_alter_post_pub_date'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='post',
            constraint=models.UniqueConstraint(fields=('title', 'text'), name='Unique person constraint'),
        ),
    ]
