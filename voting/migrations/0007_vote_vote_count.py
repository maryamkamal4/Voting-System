# Generated by Django 3.2 on 2023-08-28 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0006_pollingschedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='vote_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]