# Generated by Django 5.0.7 on 2024-08-30 08:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0045_remove_profile_ap_id_remove_profile_follows"),
    ]

    operations = [
        migrations.AlterField(
            model_name="actor",
            name="profile",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="webapp.profile",
            ),
        ),
    ]