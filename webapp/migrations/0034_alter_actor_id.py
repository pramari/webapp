# Generated by Django 5.0.4 on 2024-07-16 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0033_alter_actor_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="actor",
            name="id",
            field=models.CharField(
                max_length=255, primary_key=True, serialize=False, unique=True
            ),
        ),
    ]
