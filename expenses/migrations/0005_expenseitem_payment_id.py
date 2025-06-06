# Generated by Django 5.2.1 on 2025-05-31 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0004_add_payee_hidden_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="expenseitem",
            name="payment_id",
            field=models.CharField(
                blank=True,
                help_text="Optional payment reference ID or transaction number",
                max_length=255,
                null=True,
            ),
        ),
    ]
