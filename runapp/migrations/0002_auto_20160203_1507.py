# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-03 15:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('runapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submissionfold',
            old_name='submission_id',
            new_name='submission',
        ),
    ]