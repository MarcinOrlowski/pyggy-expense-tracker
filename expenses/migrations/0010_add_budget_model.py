# Generated manually for budget implementation

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0009_add_recurring_with_end_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="Budget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("start_date", models.DateField()),
                (
                    "initial_amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name", "created_at"],
            },
        ),
        migrations.AddField(
            model_name="month",
            name="budget",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="expenses.budget"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="month",
            unique_together={("budget", "year", "month")},
        ),
    ]
