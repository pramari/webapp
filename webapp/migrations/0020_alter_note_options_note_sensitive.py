# Generated by Django 5.0.3 on 2024-04-24 13:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("webapp", "0019_alter_action_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="note",
            options={
                "verbose_name": "Note (Activity Streams 2.0)",
                "verbose_name_plural": "Notes (Activity Streams 2.0)",
            },
        ),
        migrations.AddField(
            model_name="note",
            name="sensitive",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
