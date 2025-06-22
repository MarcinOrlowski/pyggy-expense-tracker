from django.db import models
from django.db.models import Sum  # noqa: WPS458
from django.core.exceptions import ValidationError
from decimal import Decimal


class Budget(models.Model):
    CURRENCY_CHOICES = [
        ("PLN", "PLN"),
        ("EUR", "EUR"),
        ("USD", "USD"),
    ]

    name = models.CharField(max_length=100)
    start_date = models.DateField()
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="PLN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        # For existing budgets with months, start_date cannot be changed at all
        if hasattr(self, "pk") and self.pk and not self._state.adding:
            original_budget = Budget.objects.get(pk=self.pk)
            if (
                self.start_date != original_budget.start_date
                and self.budgetmonth_set.exists()
            ):
                raise ValidationError(
                    "Start date cannot be changed when budget has existing months"
                )

    def can_be_deleted(self) -> bool:
        """Check if this budget can be deleted (no associated months)"""
        return not self.budgetmonth_set.exists()

    def get_current_balance(self) -> Decimal:
        """
        Calculate current balance: initial_amount - total_committed

        Returns:
            Decimal: Current balance (positive = remaining, negative = overcommitted)
        """
        # Import here to avoid circular imports
        from .expense_item import ExpenseItem

        # Calculate total committed from all expense items (paid + pending) in this budget
        total_committed = ExpenseItem.objects.filter(expense__budget=self).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        # Return initial amount minus total committed
        return self.initial_amount - total_committed

    def __str__(self) -> str:
        return self.name

    class Meta:
        """Meta configuration for Budget model."""

        ordering = ["name", "created_at"]
