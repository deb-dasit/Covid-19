# Generated by Django 3.0 on 2020-04-12 10:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apisv1', '0010_auto_20200412_0849'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='volunteerorder',
            name='status',
        ),
        migrations.AlterField(
            model_name='accesstoken',
            name='expire_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 12, 10, 8, 18, 208168)),
        ),
    ]