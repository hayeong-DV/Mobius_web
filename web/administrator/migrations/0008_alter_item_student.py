# Generated by Django 3.2.8 on 2021-10-30 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0007_auto_20211030_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='student',
            field=models.ForeignKey(default='none', on_delete=django.db.models.deletion.CASCADE, to='administrator.student'),
        ),
    ]
