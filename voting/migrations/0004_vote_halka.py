# Generated by Django 3.2 on 2023-08-28 07:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_customuser_halka'),
        ('voting', '0003_auto_20230828_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='halka',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='account.halka'),
        ),
    ]