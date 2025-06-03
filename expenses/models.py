from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.cache import cache
from datetime import date


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
    Expense entity supporting different payment patterns.
    
    Field Usage by Expense Type:
    
    ONE_TIME ('one_time'):
        - total_amount: Total expense amount (single payment)
        - started_at: Due date for the single payment
        - installments_count: Must be 0
        - end_date: Not used (must be None)
        - Notes: Single payment processed in start month only
    
    ENDLESS_RECURRING ('endless_recurring'):
        - total_amount: Amount charged each month
        - started_at: Start date (day of month for recurring charge)
        - installments_count: Must be 0
        - end_date: Not used (must be None)
        - Notes: Creates one expense item per month indefinitely until manually closed
    
    SPLIT_PAYMENT ('split_payment'):
        - total_amount: Monthly installment amount (not total cost)
        - started_at: Start date for first installment
        - installments_count: Total number of installments (must be > 0)
        - initial_installment: Starting installment number (0-based, default 0)
        - end_date: Not used (must be None)
        - Notes: Creates (installments_count - initial_installment) expense items, automatically closes when all paid
    
    RECURRING_WITH_END ('recurring_with_end'):
        - total_amount: Amount charged each month
        - started_at: Start date (day of month for recurring charge)
        - installments_count: Must be 0
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

    payee = models.ForeignKey(Payee, on_delete=models.PROTECT, null=True, blank=True)
    title = models.CharField(max_length=255)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    total_amount = models.DecimalField(
        max_digits=13, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    installments_count = models.PositiveIntegerField(default=0)
    initial_installment = models.PositiveIntegerField(
        default=0,
        help_text="Starting installment number (0-based). Only used for split payments."
    )
    started_at = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes or additional context about this expense"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.expense_type == self.TYPE_SPLIT_PAYMENT and self.installments_count <= 0:
            raise ValidationError('Split payments must have installments_count > 0')
        
        if self.expense_type in [self.TYPE_ENDLESS_RECURRING, self.TYPE_ONE_TIME, self.TYPE_RECURRING_WITH_END] and self.installments_count > 0:
            raise ValidationError('Only split payments can have installments_count > 0')
        
        # Validate initial_installment field
        if self.expense_type == self.TYPE_SPLIT_PAYMENT:
            if self.initial_installment < 0:
                raise ValidationError('Initial installment cannot be negative')
            if self.initial_installment >= self.installments_count:
                raise ValidationError('Initial installment must be less than total installments count')
        elif self.initial_installment > 0:
            raise ValidationError('Initial installment can only be used with split payment expenses')
        
        if self.expense_type == self.TYPE_RECURRING_WITH_END:
            if not self.end_date:
                raise ValidationError('Recurring with end date expenses must have an end date')
            if self.end_date < self.started_at:
                raise ValidationError('End date must be on or after the start date')
        
        if self.expense_type != self.TYPE_RECURRING_WITH_END and self.end_date:
            raise ValidationError('Only recurring with end date expenses can have an end date')
        
        if self.closed_at and self.closed_at > timezone.now():
            raise ValidationError('closed_at cannot be in the future')
        
        # Validate start date is not earlier than current month
        if self.started_at:
            most_recent_month = Month.get_most_recent()
            if most_recent_month:
                # Get first day of the most recent month
                current_month_start = date(most_recent_month.year, most_recent_month.month, 1)
                if self.started_at < current_month_start:
                    raise ValidationError(f'Start date cannot be earlier than the current month ({most_recent_month})')

    def calculate_payments_count(self):
        """Calculate total number of payments for recurring_with_end expenses."""
        if self.expense_type != self.TYPE_RECURRING_WITH_END or not self.end_date:
            return 0
        
        start_year, start_month = self.started_at.year, self.started_at.month
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
    
    def get_edit_restrictions(self):
        """Get detailed information about edit restrictions"""
        restrictions = {
            'can_edit': self.can_be_edited(),
            'can_edit_amount': self.can_edit_amount(),
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
        
        return restrictions

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
