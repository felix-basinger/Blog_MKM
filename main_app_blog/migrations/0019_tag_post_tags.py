# Generated by Django 5.1 on 2024-08-24 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app_blog', '0018_remove_post_tags_delete_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='posts', to='main_app_blog.tag'),
        ),
    ]
