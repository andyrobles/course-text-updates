# Generated by Django 3.0.4 on 2020-03-26 03:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='waitlist_availability',
        ),
    ]
