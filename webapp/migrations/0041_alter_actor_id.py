# Generated by Django 5.0.7 on 2024-08-04 17:05

import webapp.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0040_alter_actor_follows"),
    ]

    operations = [
        migrations.AlterField(
            model_name="actor",
            name="id",
            field=models.CharField(
                max_length=255,
                primary_key=True,
                serialize=False,
                unique=True,
                validators=[webapp.validators.validate_iri],
            ),
        ),
    ]
