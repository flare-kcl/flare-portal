# Generated by Django 3.1.5 on 2021-02-27 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0055_update_exports'),
    ]

    operations = [
        migrations.AddField(
            model_name='fearconditioningdata',
            name='did_leave_iti',
            field=models.BooleanField(default=False, verbose_name='did leave ITI'),
        ),
        migrations.AddField(
            model_name='fearconditioningdata',
            name='did_leave_task',
            field=models.BooleanField(default=False),
        ),
    ]
