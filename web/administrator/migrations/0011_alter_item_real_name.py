# Generated by Django 3.2.7 on 2021-11-11 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0010_alter_student_point_used'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='real_name',
            field=models.CharField(max_length=100),
        ),
    ]