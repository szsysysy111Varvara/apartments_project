# Generated by Django 5.0.7 on 2024-07-19 03:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentapp', '0009_alter_booking_cancellation_deadline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='cancellation_deadline',
            field=models.DateField(default=datetime.datetime(2024, 7, 20, 3, 23, 12, 425533, tzinfo=datetime.timezone.utc)),
        ),
    ]
