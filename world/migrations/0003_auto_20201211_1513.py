# Generated by Django 3.1.1 on 2020-12-11 15:13

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('world', '0002_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='address',
            field=models.CharField(default='Address', max_length=50, verbose_name='User Address'),
        ),
        migrations.AddField(
            model_name='profile',
            name='nearest_airport_code',
            field=models.CharField(max_length=3, null=True, verbose_name='Nearest Airport IATA'),
        ),
        migrations.AddField(
            model_name='profile',
            name='nearest_airport_country',
            field=models.CharField(max_length=20, null=True, verbose_name='Nearest Airport Country'),
        ),
        migrations.AddField(
            model_name='profile',
            name='nearest_airport_location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, default=None, editable=False, null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='profile',
            name='nearest_airport_name',
            field=models.CharField(max_length=50, null=True, verbose_name='Nearest Airport Info'),
        ),
    ]
