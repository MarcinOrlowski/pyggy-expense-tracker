# Generated by Django 5.2.1 on 2025-06-05 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0019_auto_20250604_0147"),
    ]

    operations = [
        migrations.AlterField(
            model_name="budget",
            name="initial_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
