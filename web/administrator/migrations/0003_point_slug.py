# Generated by Django 3.2.5 on 2021-11-30 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0002_remove_point_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='point',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, null=True),
        ),
    ]