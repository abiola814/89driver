# Generated by Django 4.0 on 2022-09-22 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_drivers_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='ownerprofiles',
            name='name',
            field=models.CharField(blank=True, max_length=900, null=True),
        ),
        migrations.AlterField(
            model_name='ownerprofiles',
            name='resturant_location',
            field=models.CharField(blank=True, max_length=199, null=True),
        ),
    ]
