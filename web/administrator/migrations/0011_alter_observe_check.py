# Generated by Django 3.2.8 on 2021-10-31 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0010_alter_item_student'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observe',
            name='check',
            field=models.CharField(choices=[('미확인', '미확인'), ('확인', '확인')], max_length=20),
        ),
    ]
