# Generated by Django 5.0.7 on 2024-07-17 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='is_active',
        ),
        migrations.AddField(
            model_name='listing',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10),
        ),
    ]
