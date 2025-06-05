from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import date
import calendar


class ExpenseItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    expense = models.ForeignKey('Expense', on_delete=models.CASCADE)
    month = models.ForeignKey('Month', on_delete=models.CASCADE)
    payment_method = models.ForeignKey(
        'PaymentMethod', on_delete=models.SET_NULL, null=True, blank=True
    )
    due_date = models.DateField()
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_id = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Optional payment reference ID or transaction number"
    )
    amount = models.DecimalField(
        max_digits=13, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Import here to avoid circular imports
        from .month import Month
        
        if self.status == 'paid' and not self.payment_date:
            raise ValidationError('Paid items must have payment_date')

        if self.status == 'pending' and self.payment_date:
            raise ValidationError('Pending items cannot have payment_date')

        # Validate due_date is within allowed range
        if self.due_date and self.expense_id:
            start_date, end_date = self.get_allowed_month_range()
            if not (start_date <= self.due_date <= end_date):
                expense_month_name = date(self.expense.start_date.year, self.expense.start_date.month, 1).strftime("%B %Y")
                if self.expense.expense_type == self.expense.TYPE_ONE_TIME:
                    most_recent_month = Month.get_most_recent(budget=self.expense.budget)
                    if most_recent_month and start_date < date(self.expense.start_date.year, self.expense.start_date.month, 1):
                        active_month_name = date(most_recent_month.year, most_recent_month.month, 1).strftime("%B %Y")
                        raise ValidationError(f'Due date must be between {active_month_name} and {expense_month_name}')
                    else:
                        raise ValidationError(f'Due date must be within {expense_month_name}')
                else:
                    raise ValidationError(f'Due date must be within {expense_month_name}')

    def get_allowed_month_range(self):
        """Returns (start_date, end_date) tuple for allowed month range based on expense type and creation month"""
        # Import here to avoid circular imports
        from .month import Month
        
        if not self.expense_id:
            return None, None

        expense_month = self.expense.start_date
        year, month = expense_month.year, expense_month.month

        # For one-time expenses, allow moving as early as the most recent month in budget
        if self.expense.expense_type == self.expense.TYPE_ONE_TIME:
            # Get the most recent (active) month for this budget
            most_recent_month = Month.get_most_recent(budget=self.expense.budget)
            if most_recent_month:
                # Start date is the earlier of: expense creation month or most recent month
                active_month_start = date(most_recent_month.year, most_recent_month.month, 1)
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
    def days_until_due(self):
        """Calculate days until due date from today"""
        today = date.today()
        delta = (self.due_date - today).days
        return delta

    def __str__(self):
        return f"{self.expense.title} - {self.month} - {self.status}"

    class Meta:
        ordering = ['due_date', '-created_at']