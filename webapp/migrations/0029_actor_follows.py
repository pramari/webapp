# Generated by Django 5.0.4 on 2024-06-26 11:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("webapp", "0028_actor_preferredusername"),
    ]

    operations = [
        migrations.AddField(
            model_name="actor",
            name="follows",
            field=models.ManyToManyField(
                blank=True, related_name="followed_by", to="webapp.actor"
            ),
        ),
    ]
