# Generated by Django 5.1 on 2024-08-12 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app_blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='preview',
            field=models.TextField(default='No preview available', max_length=300),
        ),
    ]
