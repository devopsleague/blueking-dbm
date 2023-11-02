# Generated by Django 3.2.19 on 2023-11-01 09:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("db_package", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="package",
            name="create_at",
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name="创建时间"),
        ),
        migrations.AlterField(
            model_name="package",
            name="update_at",
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name="更新时间"),
        ),
    ]