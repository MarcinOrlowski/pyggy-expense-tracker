# Generated by Django 5.2.1 on 2025-05-31 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0002_remove_expense_payment_method_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="expenseitem",
            name="payment_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
