# Generated manually for bind-expense-to-budget feature

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0015_add_initial_installment_to_expense"),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="budget",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="expenses.budget"
            ),
            preserve_default=False,
        ),
    ]
