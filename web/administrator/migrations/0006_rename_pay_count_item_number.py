# Generated by Django 3.2.8 on 2021-10-30 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0005_remove_item_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='pay_count',
            new_name='number',
        ),
    ]