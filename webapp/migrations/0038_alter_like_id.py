# Generated by Django 5.0.7 on 2024-07-22 15:17

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0037_like"),
    ]

    operations = [
        migrations.AlterField(
            model_name="like",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False  # noqa
            ),
        ),
    ]
