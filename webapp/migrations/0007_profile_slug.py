# Generated by Django 4.1 on 2023-02-20 14:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("webapp", "0006_profile_mastodon_alter_profile_img"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="slug",
            field=models.SlugField(null=True),
        ),
    ]
