# Generated by Django 3.2.16 on 2024-04-02 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0022_alter_post_pub_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('created_at',), 'verbose_name': 'комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
    ]