# Generated by Django 5.0.7 on 2024-07-19 05:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentapp', '0012_alter_booking_cancellation_deadline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='cancellation_deadline',
            field=models.DateField(default=datetime.datetime(2024, 7, 20, 5, 47, 57, 968186, tzinfo=datetime.timezone.utc)),
        ),
    ]
