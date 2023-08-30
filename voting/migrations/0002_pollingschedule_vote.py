# Generated by Django 3.2 on 2023-08-27 12:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0002_customuser_halka'),
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PollingSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes_received', to=settings.AUTH_USER_MODEL)),
                ('halka', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.halka')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes_given', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]