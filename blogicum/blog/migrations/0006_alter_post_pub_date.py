# Generated by Django 3.2.16 on 2023-12-04 15:12

import blog.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_delete_blogcreate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(help_text='Если установить дату и время в будущем — можно делать отложенные публикации.', validators=[blog.validators.age_protect], verbose_name='Дата и время публикации'),
        ),
    ]