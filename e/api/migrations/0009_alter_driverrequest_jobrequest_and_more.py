# Generated by Django 4.0 on 2022-10-10 08:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_driverrequest_status_alter_jobrequest_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverrequest',
            name='jobrequest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobrequesting', to='api.jobrequest'),
        ),
        migrations.AlterField(
            model_name='driverrequest',
            name='status',
            field=models.CharField(choices=[('Request', 'Request'), ('Accept', 'Accept'), ('Completed', 'Completed'), ('Declined', 'Declined')], default='Request', max_length=20),
        ),
    ]