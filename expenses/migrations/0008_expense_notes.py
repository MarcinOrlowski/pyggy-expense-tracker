# Generated by Django 5.2.1 on 2025-06-01 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0007_add_settings_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="notes",
            field=models.TextField(
                blank=True,
                help_text="Optional notes or additional context about this expense",
                null=True,
            ),
        ),
    ]
