# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-18 20:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('runapp', '0010_auto_20160217_1646'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionfold',
            name='task_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]