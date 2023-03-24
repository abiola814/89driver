# Generated by Django 4.0 on 2022-10-08 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_jobrequest_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverrequest',
            name='status',
            field=models.CharField(choices=[('Request', 'Request'), ('Accept', 'Accept'), ('completed', 'Completed')], default='Request', max_length=20),
        ),
        migrations.AlterField(
            model_name='jobrequest',
            name='status',
            field=models.CharField(choices=[('creating', 'Creating'), ('active', 'active'), ('Delivered', 'Delivered'), ('cancelled', 'cancel'), ('completed', 'Completed'), ('pending', 'pending')], default='creating', max_length=255),
        ),
    ]
