# Generated by Django 5.1.3 on 2025-01-03 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0048_remove_user_consent_remove_user_public"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="publish_to_linkedin",
            field=models.BooleanField(default=False),
        ),
    ]
