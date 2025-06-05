from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
import calendar


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
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE)
    payee = models.ForeignKey('Payee', on_delete=models.PROTECT, null=True, blank=True)
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

    def clean(self) -> None:
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
        # Import here to avoid circular imports
        from .month import Month
        
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

    def calculate_payments_count(self) -> int:
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

    def get_expense_type_icon(self) -> str:
        """Get Font Awesome icon class for the expense type."""
        return self.EXPENSE_TYPE_ICONS.get(self.expense_type, 'fa-question-circle')
    
    def get_expense_type_icon_css_class(self) -> str:
        """Get CSS class for expense type icon color."""
        return f'expense-type-icon-{self.expense_type.replace("_", "-")}'

    def can_be_deleted(self) -> bool:
        """Check if this expense can be deleted (no paid expense items)"""
        return not self.expenseitem_set.filter(status='paid').exists()

    def can_be_edited(self) -> bool:
        """Check if this expense can be edited at all"""
        # Cannot edit if expense is closed
        if self.closed_at:
            return False

        # Cannot edit recurring expenses (split payment or recurring with end date)
        if self.expense_type in [self.TYPE_SPLIT_PAYMENT, self.TYPE_RECURRING_WITH_END]:
            return False

        # One-time and endless recurring expenses can be edited (with restrictions)
        return True

    def can_edit_amount(self) -> bool:
        """Check if the amount field can be edited"""
        # First check if expense can be edited at all
        if not self.can_be_edited():
            return False

        # Cannot edit amount if any expense item is paid
        has_paid_items = self.expenseitem_set.filter(status='paid').exists()
        if has_paid_items:
            return False

        return True

    def can_edit_date(self) -> bool:
        """Check if the start date can be edited based on current date restrictions"""
        # Import here to avoid circular imports
        from .month import Month
        
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

    def get_next_month_date(self) -> Optional[date]:
        """Calculate next month start date for this expense's budget"""
        # Import here to avoid circular imports
        from .month import Month
        
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

    def get_edit_restrictions(self) -> Dict[str, Union[bool, List[str]]]:
        """Get detailed information about edit restrictions"""
        restrictions: Dict[str, Union[bool, List[str]]] = {
            'can_edit': self.can_be_edited(),
            'can_edit_amount': self.can_edit_amount(),
            'can_edit_date': self.can_edit_date(),
            'reasons': []
        }

        reasons_list = restrictions['reasons']
        assert isinstance(reasons_list, list)  # Type narrowing for mypy
        
        if self.closed_at:
            reasons_list.append('Expense is closed')

        if self.expense_type == self.TYPE_SPLIT_PAYMENT:
            reasons_list.append('Split payment expenses cannot be edited')
        elif self.expense_type == self.TYPE_RECURRING_WITH_END:
            reasons_list.append('Recurring expenses with end date cannot be edited')

        if restrictions['can_edit'] and not restrictions['can_edit_amount']:
            has_paid_items = self.expenseitem_set.filter(status='paid').exists()
            if has_paid_items:
                reasons_list.append('Amount cannot be edited because expense has paid items')

        if restrictions['can_edit'] and not restrictions['can_edit_date']:
            reasons_list.append('Date cannot be edited for expenses earlier than next month')

        return restrictions

    def get_due_date_for_month(self, year: int, month: int) -> date:
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
    
    def calculate_total_cost(self) -> Decimal:
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
    
    def get_remaining_parts(self) -> int:
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

    def __str__(self) -> str:
        if self.payee:
            return f"{self.title} - {self.payee.name}"
        return self.title

    class Meta:
        ordering = ['-created_at']