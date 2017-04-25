# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-03-29 18:56
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0074_fill_allocationsource_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationsource',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]