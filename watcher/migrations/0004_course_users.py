# Generated by Django 2.2.1 on 2020-03-22 06:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('watcher', '0003_course_seating_availability'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='users',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
