# Generated by Django 5.1 on 2024-08-15 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app_blog', '0008_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
