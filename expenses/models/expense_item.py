from django.db import models
from django.db.models import Sum  # noqa: WPS458
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import date
from typing import Tuple
from decimal import Decimal
import calendar


class ExpenseItem(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
    ]

    expense = models.ForeignKey("Expense", on_delete=models.CASCADE)
    month = models.ForeignKey("BudgetMonth", on_delete=models.CASCADE)
    due_date = models.DateField()
    amount = models.DecimalField(
        max_digits=13, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        # Import here to avoid circular imports
        from .month import BudgetMonth

        # Validate due_date is within allowed range
        if self.due_date and self.expense_id:
            start_date, end_date = self.get_allowed_month_range()
            if not (start_date <= self.due_date <= end_date):
                expense_month_name = date(
                    self.expense.start_date.year, self.expense.start_date.month, 1
                ).strftime("%B %Y")
                if self.expense.expense_type == self.expense.TYPE_ONE_TIME:
                    most_recent_month = BudgetMonth.get_most_recent(
                        budget=self.expense.budget
                    )
                    if most_recent_month and start_date < date(
                        self.expense.start_date.year, self.expense.start_date.month, 1
                    ):
                        active_month_name = date(
                            most_recent_month.year, most_recent_month.month, 1
                        ).strftime("%B %Y")
                        raise ValidationError(
                            f"Due date must be between {active_month_name} and {expense_month_name}"
                        )
                    else:
                        raise ValidationError(
                            f"Due date must be within {expense_month_name}"
                        )
                else:
                    raise ValidationError(
                        f"Due date must be within {expense_month_name}"
                    )

    def get_allowed_month_range(self) -> Tuple[date, date]:
        """Returns (start_date, end_date) tuple for allowed month range based on expense type and creation month"""
        # Import here to avoid circular imports
        from .month import BudgetMonth

        if not self.expense_id:
            raise ValueError("Cannot determine allowed month range without an expense")

        expense_month = self.expense.start_date
        year, month = expense_month.year, expense_month.month

        # For one-time expenses, allow moving as early as the most recent month in budget
        if self.expense.expense_type == self.expense.TYPE_ONE_TIME:
            # Get the most recent (active) month for this budget
            most_recent_month = BudgetMonth.get_most_recent(budget=self.expense.budget)
            if most_recent_month:
                # Start date is the earlier of: expense creation month or most recent month
                active_month_start = date(
                    most_recent_month.year, most_recent_month.month, 1
                )
                expense_month_start = date(year, month, 1)
                start_date = min(active_month_start, expense_month_start)
            else:
                start_date = date(year, month, 1)
        else:
            # For other expense types, restrict to creation month only
            start_date = date(year, month, 1)

        # End date is always the last day of the expense creation month
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        return start_date, end_date

    @property
    def days_until_due(self) -> int:
        """Calculate days until due date from today"""
        today = date.today()
        delta = (self.due_date - today).days
        return delta

    def get_total_paid(self) -> Decimal:
        """Calculate total amount paid from all Payment records"""
        total = self.payment_set.aggregate(Sum("amount"))["amount__sum"]
        return total or Decimal("0.00")

    def get_remaining_amount(self) -> Decimal:
        """Calculate remaining amount to be paid (negative = still owed, positive = overpaid)"""
        return self.get_total_paid() - self.amount

    def get_payment_count(self) -> int:
        """Get the number of payments made for this expense item"""
        return self.payment_set.count()

    @property
    def status(self) -> str:
        """Calculate payment status based on total payments"""
        return (
            self.STATUS_PAID
            if self.get_total_paid() >= self.amount
            else self.STATUS_PENDING
        )

    def is_fully_paid(self) -> bool:
        """Check if expense item is fully paid"""
        return self.get_total_paid() >= self.amount

    def can_be_deleted(self) -> bool:
        """Check if expense item can be deleted.

        Returns True if:
        - No payment records exist (get_payment_count() == 0)
        - Expense is one-time type
        - Item belongs to current month
        """
        # Import here to avoid circular imports
        from .month import BudgetMonth

        # Must have no payment records
        if self.get_payment_count() > 0:
            return False

        # Must be a one-time expense
        if self.expense.expense_type != self.expense.TYPE_ONE_TIME:
            return False

        # Must be from current (most recent) month
        current_month = BudgetMonth.get_most_recent(budget=self.expense.budget)
        if not current_month or self.month != current_month:
            return False

        return True

    def __str__(self) -> str:
        return f"{self.expense.title} - {self.month} - {self.status}"

    class Meta:
        """Meta configuration for ExpenseItem model."""

        ordering = ["due_date", "-created_at"]
