from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.cache import cache
from datetime import date


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
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2099)]
    )
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.year}-{self.month:02d}"
    
    def has_paid_expenses(self):
        """Check if this month has any paid expense items"""
        return self.expenseitem_set.filter(status='paid').exists()
    
    def can_delete(self):
        """Check if this month can be deleted (no paid expenses)"""
        return not self.has_paid_expenses()
    
    @classmethod
    def get_most_recent(cls):
        """Get the most recent month in the system"""
        return cls.objects.first()  # Due to ordering, first() returns most recent
    
    @classmethod
    def get_next_allowed_month(cls):
        """Calculate the next month that can be created"""
        most_recent = cls.get_most_recent()
        if not most_recent:
            return None  # No months exist, need initial seeding
        
        if most_recent.month == 12:
            return {'year': most_recent.year + 1, 'month': 1}
        else:
            return {'year': most_recent.year, 'month': most_recent.month + 1}


class Expense(models.Model):
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

    payee = models.ForeignKey(Payee, on_delete=models.PROTECT, null=True, blank=True)
    title = models.CharField(max_length=255)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    total_amount = models.DecimalField(
        max_digits=13, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    installments_count = models.PositiveIntegerField(default=0)
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
