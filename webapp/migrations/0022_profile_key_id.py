# Generated by Django 5.0.4 on 2024-06-12 12:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("webapp", "0021_alter_profile_ap_id_alter_profile_private_key_pem"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="key_id",
            field=models.CharField(
                blank=True, help_text="Key ID", max_length=255
            ),  # noqa: E501
        ),
    ]
