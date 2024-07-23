# Generated by Django 5.0.7 on 2024-07-22 07:58

import django.db.models.deletion
import webapp.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0036_note_attributedto_note_contentmap_note_remoteid"),
    ]

    operations = [
        migrations.CreateModel(
            name="Like",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "object",
                    models.URLField(validators=[webapp.validators.validate_iri]),  # noqa: E501
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="webapp.actor"  # noqa: E501
                    ),
                ),
            ],
        ),
    ]