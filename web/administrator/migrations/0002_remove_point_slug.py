# Generated by Django 3.2.5 on 2021-11-30 02:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='point',
            name='slug',
        ),
    ]