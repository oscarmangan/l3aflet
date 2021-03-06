# Generated by Django 3.1.1 on 2020-12-12 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('world', '0003_auto_20201211_1513'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='address',
        ),
        migrations.AddField(
            model_name='profile',
            name='country',
            field=models.CharField(default='Country', max_length=50, verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='profile',
            name='county',
            field=models.CharField(default='County', max_length=50, verbose_name='County'),
        ),
        migrations.AddField(
            model_name='profile',
            name='locale',
            field=models.CharField(default='Locale', max_length=50, verbose_name='Locale'),
        ),
        migrations.AddField(
            model_name='profile',
            name='road',
            field=models.CharField(default='Road', max_length=50, verbose_name='Road'),
        ),
    ]
