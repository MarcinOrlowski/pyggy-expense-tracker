from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.cache import cache
from datetime import date
import calendar


class Budget(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    initial_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.start_date and self.start_date < date.today():
            # Allow past dates only if this budget has no months
            if hasattr(self, 'pk') and self.pk:
                if self.month_set.exists():
                    raise ValidationError('Start date cannot be in the past when budget has existing months')

    def can_be_deleted(self):
        """Check if this budget can be deleted (no associated months)"""
        return not self.month_set.exists()

    def get_current_balance(self):
        """
        Calculate current balance: initial_amount - total_committed
        
        Returns:
            Decimal: Current balance (positive = remaining, negative = overcommitted)
        """
        from decimal import Decimal
        from django.db.models import Sum
        
        # Calculate total committed from all expense items (paid + pending) in this budget
        total_committed = ExpenseItem.objects.filter(
            expense__budget=self
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Return initial amount minus total committed
        return self.initial_amount - total_committed

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', 'created_at']


class Payee(models.Model):
    name = models.CharField(max_length=255, unique=True)
    hidden_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_hidden(self):
        return self.hidden_at is not None

    def can_be_deleted(self):
        """Check if this payee can be deleted (no associated expenses and not hidden)"""
        return not self.expense_set.exists() and not self.is_hidden

    class Meta:
        ordering = ['name']


class PaymentMethod(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Month(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2099)]
    )
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['budget', 'year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.year}-{self.month:02d}"

    def has_paid_expenses(self):
        """Check if this month has any paid expense items"""
        return self.expenseitem_set.filter(status='paid').exists()

    def can_be_deleted(self):
        """Check if this month can be deleted (no paid expenses)"""
        return not self.has_paid_expenses()

    @classmethod
    def get_most_recent(cls, budget=None):
        """Get the most recent month in the system or for a specific budget"""
        if budget:
            return cls.objects.filter(budget=budget).first()
        return cls.objects.first()  # Due to ordering, first() returns most recent

    @classmethod
    def get_next_allowed_month(cls, budget=None):
        """Calculate the next month that can be created"""
        most_recent = cls.get_most_recent(budget)
        if not most_recent:
            return None  # No months exist, need initial seeding

        if most_recent.month == 12:
            return {'year': most_recent.year + 1, 'month': 1}
        else:
            return {'year': most_recent.year, 'month': most_recent.month + 1}


class Expense(models.Model):
    """
    Expense schedule definition - defines WHEN and HOW MUCH to pay.
    Individual payment instances are represented by ExpenseItem objects.
    
    Field Usage by Expense Type:
    
    ONE_TIME ('one_time'):
        - amount: Total expense amount (single payment)
        - start_date: When the single payment is due
        - day_of_month: Extracted from start_date.day
        - total_parts: Must be 0
        - skip_parts: Must be 0
        - end_date: Not used (must be None)
        - Notes: Single payment processed in start month only
    
    ENDLESS_RECURRING ('endless_recurring'):
        - amount: Amount charged each month
        - start_date: When recurring payments begin
        - day_of_month: Day of month for recurring charges (with fallback logic)
        - total_parts: Must be 0
        - skip_parts: Must be 0
        - end_date: Not used (must be None)
        - Notes: Creates one expense item per month indefinitely until manually closed
    
    SPLIT_PAYMENT ('split_payment'):
        - amount: Amount per installment (not total cost)
        - start_date: Start date for first installment
        - day_of_month: Day of month for each installment
        - total_parts: Total number of installments (must be > 0)
        - skip_parts: Number of initial parts to skip (0-based, default 0)
        - end_date: Not used (must be None)
        - Notes: Creates (total_parts - skip_parts) expense items, automatically closes when all paid
    
    RECURRING_WITH_END ('recurring_with_end'):
        - amount: Amount charged each month
        - start_date: When recurring payments begin
        - day_of_month: Day of month for recurring charges (with fallback logic)
        - total_parts: Must be 0
        - skip_parts: Must be 0
        - end_date: Last month to create charges (required)
        - Notes: Creates one expense item per month until end_date month (inclusive)
    """

    # Expense type constants
    TYPE_ENDLESS_RECURRING = 'endless_recurring'
    TYPE_SPLIT_PAYMENT = 'split_payment'
    TYPE_ONE_TIME = 'one_time'
    TYPE_RECURRING_WITH_END = 'recurring_with_end'

    EXPENSE_TYPES = [
        (TYPE_ENDLESS_RECURRING, 'Endless Recurring'),
        (TYPE_SPLIT_PAYMENT, 'Split Payment'),
        (TYPE_ONE_TIME, 'One Time'),
        (TYPE_RECURRING_WITH_END, 'Recurring with End Date'),
    ]

    EXPENSE_TYPE_ICONS = {
        TYPE_ENDLESS_RECURRING: 'fa-arrows-rotate',
        TYPE_SPLIT_PAYMENT: 'fa-money-bill-transfer',
        TYPE_ONE_TIME: 'fa-circle-dot',
        TYPE_RECURRING_WITH_END: 'fa-calendar-check'
    }

    # Core expense information
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    payee = models.ForeignKey(Payee, on_delete=models.PROTECT, null=True, blank=True)
    title = models.CharField(max_length=255)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    
    # Core scheduling fields
    amount = models.DecimalField(
        max_digits=13, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Per-installment amount for split payments, total amount for others"
    )
    start_date = models.DateField(
        help_text="When this expense schedule begins (renamed from started_at)"
    )
    day_of_month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Day of month when payment is due (fallback logic for shorter months)"
    )
    
    # Split payment specific fields  
    total_parts = models.PositiveIntegerField(
        default=0,
        help_text="Total number of installments for split payments (renamed from installments_count)"
    )
    skip_parts = models.PositiveIntegerField(
        default=0, 
        help_text="Number of initial parts to skip - for tracking remaining payments (renamed from initial_installment)"
    )
    
    # Recurring with end date specific field
    end_date = models.DateField(
        null=True, blank=True,
        help_text="Last month to create charges (only for recurring_with_end type)"
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes or additional context about this expense"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Validate expense data based on type-specific business rules.
        
        Validation Rules:
        1. Split payments must have total_parts > 0
        2. Non-split payments must have total_parts = 0
        3. skip_parts must be valid for split payments (0 <= skip_parts < total_parts)
        4. day_of_month must be valid (1-31)
        5. Recurring with end date must have end_date
        6. Only recurring with end date can have end_date
        """
        # Validate total_parts field
        if self.expense_type == self.TYPE_SPLIT_PAYMENT and self.total_parts <= 0:
            raise ValidationError('Split payments must have total_parts > 0')

        if self.expense_type in [self.TYPE_ENDLESS_RECURRING, self.TYPE_ONE_TIME, self.TYPE_RECURRING_WITH_END] and self.total_parts > 0:
            raise ValidationError('Only split payments can have total_parts > 0')

        # Validate skip_parts field
        if self.expense_type == self.TYPE_SPLIT_PAYMENT:
            if self.skip_parts < 0:
                raise ValidationError('Skip parts cannot be negative')
            if self.skip_parts >= self.total_parts:
                raise ValidationError('Skip parts must be less than total parts count')
        elif self.skip_parts > 0:
            raise ValidationError('Skip parts can only be used with split payment expenses')

        # Validate end_date field
        if self.expense_type == self.TYPE_RECURRING_WITH_END:
            if not self.end_date:
                raise ValidationError('Recurring with end date expenses must have an end date')
            if self.end_date < self.start_date:
                raise ValidationError('End date must be on or after the start date')

        if self.expense_type != self.TYPE_RECURRING_WITH_END and self.end_date:
            raise ValidationError('Only recurring with end date expenses can have an end date')

        if self.closed_at and self.closed_at > timezone.now():
            raise ValidationError('closed_at cannot be in the future')

        # Validate start date is not earlier than current month for this budget
        if self.start_date and self.budget_id:
            most_recent_month = Month.get_most_recent(budget=self.budget)
            if most_recent_month:
                # Get first day of the most recent month
                current_month_start = date(most_recent_month.year, most_recent_month.month, 1)
                if self.start_date < current_month_start:
                    raise ValidationError(f'Start date cannot be earlier than the current month ({most_recent_month})')

    def calculate_payments_count(self):
        """
        Calculate total number of payments for recurring_with_end expenses.
        
        Returns:
            int: Number of monthly payments from start_date to end_date (inclusive)
            0 for non-recurring_with_end types or when end_date is not set
        """
        if self.expense_type != self.TYPE_RECURRING_WITH_END or not self.end_date:
            return 0

        start_year, start_month = self.start_date.year, self.start_date.month
        end_year, end_month = self.end_date.year, self.end_date.month

        # Calculate months between start and end (inclusive)
        total_months = (end_year - start_year) * 12 + (end_month - start_month) + 1
        return max(0, total_months)

    def get_expense_type_icon(self):
        """Get Font Awesome icon class for the expense type."""
        return self.EXPENSE_TYPE_ICONS.get(self.expense_type, 'fa-question-circle')

    def can_be_deleted(self):
        """Check if this expense can be deleted (no paid expense items)"""
        return not self.expenseitem_set.filter(status='paid').exists()

    def can_be_edited(self):
        """Check if this expense can be edited at all"""
        # Cannot edit if expense is closed
        if self.closed_at:
            return False

        # Cannot edit recurring expenses (split payment or recurring with end date)
        if self.expense_type in [self.TYPE_SPLIT_PAYMENT, self.TYPE_RECURRING_WITH_END]:
            return False

        # One-time and endless recurring expenses can be edited (with restrictions)
        return True

    def can_edit_amount(self):
        """Check if the amount field can be edited"""
        # First check if expense can be edited at all
        if not self.can_be_edited():
            return False

        # Cannot edit amount if any expense item is paid
        has_paid_items = self.expenseitem_set.filter(status='paid').exists()
        if has_paid_items:
            return False

        return True

    def can_edit_date(self):
        """Check if the start date can be edited based on current date restrictions"""
        # First check if expense can be edited at all
        if not self.can_be_edited():
            return False

        # For one-time expenses, allow editing dates back to the most recent month
        if self.expense_type == self.TYPE_ONE_TIME:
            return True

        # For other expense types, check if current expense date is not earlier than next month
        if self.start_date and self.budget_id:
            most_recent_month = Month.get_most_recent(budget=self.budget)
            if most_recent_month:
                # Calculate next month start date
                if most_recent_month.month == 12:
                    next_month_start = date(most_recent_month.year + 1, 1, 1)
                else:
                    next_month_start = date(most_recent_month.year, most_recent_month.month + 1, 1)

                # Can only edit date if current expense date is not earlier than next month
                if self.start_date < next_month_start:
                    return False

        return True

    def get_next_month_date(self):
        """Calculate next month start date for this expense's budget"""
        if not self.budget_id:
            return None

        most_recent_month = Month.get_most_recent(budget=self.budget)
        if not most_recent_month:
            return None

        # Calculate next month (current active month + 1)
        if most_recent_month.month == 12:
            return date(most_recent_month.year + 1, 1, 1)
        else:
            return date(most_recent_month.year, most_recent_month.month + 1, 1)

    def get_edit_restrictions(self):
        """Get detailed information about edit restrictions"""
        restrictions = {
            'can_edit': self.can_be_edited(),
            'can_edit_amount': self.can_edit_amount(),
            'can_edit_date': self.can_edit_date(),
            'reasons': []
        }

        if self.closed_at:
            restrictions['reasons'].append('Expense is closed')

        if self.expense_type == self.TYPE_SPLIT_PAYMENT:
            restrictions['reasons'].append('Split payment expenses cannot be edited')
        elif self.expense_type == self.TYPE_RECURRING_WITH_END:
            restrictions['reasons'].append('Recurring expenses with end date cannot be edited')

        if restrictions['can_edit'] and not restrictions['can_edit_amount']:
            has_paid_items = self.expenseitem_set.filter(status='paid').exists()
            if has_paid_items:
                restrictions['reasons'].append('Amount cannot be edited because expense has paid items')

        if restrictions['can_edit'] and not restrictions['can_edit_date']:
            restrictions['reasons'].append('Date cannot be edited for expenses earlier than next month')

        return restrictions

    def get_due_date_for_month(self, year, month):
        """
        Calculate actual due date for a given month, handling months with fewer days.
        
        Examples:
        - day_of_month=15: Always returns 15th (all months have 15+ days)
        - day_of_month=30 in February: Returns 28th/29th (Feb's last day)
        - day_of_month=31 in April: Returns 30th (April's last day)
        
        Args:
            year (int): Year for the target month
            month (int): Month (1-12) for the target date
            
        Returns:
            date: Actual due date with day-of-month fallback applied
            
        Logic: Use min(requested_day, last_day_of_month)
        """
        last_day_of_month = calendar.monthrange(year, month)[1]
        actual_day = min(self.day_of_month, last_day_of_month)
        return date(year, month, actual_day)
    
    def calculate_total_cost(self):
        """
        Calculate total cost based on expense type.
        
        Returns:
            Decimal: Total cost of the expense
            
        Logic:
        - SPLIT_PAYMENT: amount × total_parts (sum of all installments)
        - Others: amount (already represents the total cost)
        """
        if self.expense_type == self.TYPE_SPLIT_PAYMENT:
            return self.amount * self.total_parts
        return self.amount
    
    def get_remaining_parts(self):
        """
        For split payments: calculate how many parts are still pending.
        
        Returns:
            int: Number of remaining installments
            0 for non-split payment types
            
        Used to determine how many payments are still pending.
        Formula: total_parts - skip_parts
        """
        if self.expense_type == self.TYPE_SPLIT_PAYMENT:
            return max(0, self.total_parts - self.skip_parts)
        return 0

    def __str__(self):
        if self.payee:
            return f"{self.title} - {self.payee.name}"
        return self.title

    class Meta:
        ordering = ['-created_at']


class ExpenseItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True
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


class Settings(models.Model):
    """Application-wide settings singleton model."""

    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text='ISO 4217 currency code'
    )

    locale = models.CharField(
        max_length=10,
        default='en_US',
        help_text='Locale identifier (e.g., en_US, fr_FR)'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

    def save(self, *args, **kwargs):
        """Ensure only one Settings instance exists."""
        self.pk = 1
        super().save(*args, **kwargs)
        # Clear cache when settings are saved
        cache.delete('app_settings')

    def delete(self, *args, **kwargs):
        """Prevent deletion of settings."""
        pass

    @classmethod
    def load(cls):
        """Load or create settings instance."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
