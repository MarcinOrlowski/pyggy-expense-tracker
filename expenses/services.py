from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional, Union
from babel.numbers import format_currency as babel_format_currency
from babel.core import Locale
from .models import Expense, ExpenseItem, Month, Settings, Budget


def process_new_month(year: int, month: int, budget: Budget) -> Month:
    """
    Create new month and generate expense items for active expenses.

    Args:
        year: Target year (2020-2099)
        month: Target month (1-12)
        budget: The budget to create the month in

    Returns:
        Month: Created or existing month instance

    Raises:
        ValidationError: If month already processed
        ValueError: If invalid year/month
    """
    if not (2020 <= year <= 2099):
        raise ValueError("Year must be between 2020 and 2099")

    if not (1 <= month <= 12):
        raise ValueError("Month must be between 1 and 12")

    with transaction.atomic():
        month_obj, created = Month.objects.get_or_create(
            budget=budget, year=year, month=month
        )

        if created:
            # Generate expense items for all active expenses in this budget
            active_expenses = Expense.objects.filter(
                closed_at__isnull=True, budget=budget
            )

            for expense in active_expenses:
                create_expense_items_for_month(expense, month_obj)

        return month_obj


def create_expense_items_for_month(expense: Expense, month: Month) -> List[ExpenseItem]:
    """
    Generate appropriate expense items for given expense and month.

    Business Rules:
    - endless_recurring: Create one item per month
    - split_payment: Create items until installments_count reached
    - one_time: Create single item only in start month
    - recurring_with_end: Create one item per month until end date month
    """
    items: List[ExpenseItem] = []
    expense_start_date = expense.start_date

    # Check if the expense is relevant for this month
    # For other expense types (not one-time), check start date
    import calendar

    last_day = calendar.monthrange(month.year, month.month)[1]
    month_end_date = date(month.year, month.month, last_day)

    if expense.expense_type != expense.TYPE_ONE_TIME:
        # For other expense types, check if start date is after this month
        if expense_start_date > month_end_date:
            return items

    if expense.expense_type == expense.TYPE_ENDLESS_RECURRING:
        # Create one item per month
        due_date = expense.get_due_date_for_month(month.year, month.month)

        item = ExpenseItem.objects.create(
            expense=expense, month=month, due_date=due_date, amount=expense.amount
        )
        items.append(item)

    elif expense.expense_type == expense.TYPE_RECURRING_WITH_END:
        # Create one item per month until end date month (inclusive)
        if expense.end_date is not None:
            target_date = date(month.year, month.month, 1)
            end_month_date = date(expense.end_date.year, expense.end_date.month, 1)

            if target_date <= end_month_date:
                due_date = expense.get_due_date_for_month(month.year, month.month)

                item = ExpenseItem.objects.create(
                    expense=expense,
                    month=month,
                    due_date=due_date,
                    amount=expense.amount,
                )
                items.append(item)

    elif expense.expense_type == expense.TYPE_SPLIT_PAYMENT:
        # Check how many items we've already created
        existing_count = ExpenseItem.objects.filter(expense=expense).count()
        remaining_installments = expense.total_parts - expense.skip_parts

        if existing_count < remaining_installments:
            due_date = expense.get_due_date_for_month(month.year, month.month)

            item = ExpenseItem.objects.create(
                expense=expense, month=month, due_date=due_date, amount=expense.amount
            )
            items.append(item)

    elif expense.expense_type == expense.TYPE_ONE_TIME:
        # For one-time expenses, create item if no items exist yet
        # The month being processed determines the due_date
        if not ExpenseItem.objects.filter(expense=expense).exists():
            due_date = expense.get_due_date_for_month(month.year, month.month)

            item = ExpenseItem.objects.create(
                expense=expense, month=month, due_date=due_date, amount=expense.amount
            )
            items.append(item)

    return items


def check_expense_completion(expense: Expense) -> bool:
    """
    Check if expense should be marked as complete.

    Rules:
    - one_time: Complete when single item is paid
    - split_payment: Complete when all installments paid
    - endless_recurring: Manual completion only
    - recurring_with_end: Manual completion only
    """
    from .models import Payment
    
    if expense.closed_at:
        return True  # Already completed

    if expense.expense_type == expense.TYPE_ONE_TIME:
        # Complete when the single item is paid (has Payment records totaling full amount)
        expense_items = ExpenseItem.objects.filter(expense=expense)
        paid_items = sum(1 for item in expense_items if item.status == ExpenseItem.STATUS_PAID)
        if paid_items > 0:
            expense.closed_at = timezone.now()
            expense.save()
            return True

    elif expense.expense_type == expense.TYPE_SPLIT_PAYMENT:
        # Complete when all remaining installments are paid
        expense_items = ExpenseItem.objects.filter(expense=expense)
        paid_items = sum(1 for item in expense_items if item.status == ExpenseItem.STATUS_PAID)
        remaining_installments = expense.total_parts - expense.skip_parts
        if paid_items >= remaining_installments:
            expense.closed_at = timezone.now()
            expense.save()
            return True

    # endless_recurring and recurring_with_end expenses are only manually completed
    return False


def handle_new_expense(expense: Expense, budget: Budget) -> None:
    """
    Handle newly created expense - create expense items if it starts/is due in current month.

    Args:
        expense: The newly created expense
        budget: The budget to use for finding the most recent month (should match expense.budget)
    """
    most_recent_month = (
        Month.objects.filter(budget=expense.budget).order_by("-year", "-month").first()
    )
    if not most_recent_month:
        return  # No months exist yet in this budget

    # For one-time expenses, always try to create in the current month
    # For other expense types, check if start date falls in current month
    if expense.expense_type == expense.TYPE_ONE_TIME:
        create_expense_items_for_month(expense, most_recent_month)
    else:
        check_date = expense.start_date

        current_month_start = date(most_recent_month.year, most_recent_month.month, 1)

        import calendar

        last_day = calendar.monthrange(most_recent_month.year, most_recent_month.month)[
            1
        ]
        current_month_end = date(
            most_recent_month.year, most_recent_month.month, last_day
        )

        # If expense starts within the current month, create expense items immediately
        if current_month_start <= check_date <= current_month_end:
            create_expense_items_for_month(expense, most_recent_month)


class SettingsService:
    """Service for managing application settings and currency formatting."""

    CACHE_KEY = "app_settings"
    CACHE_TIMEOUT = 3600  # 1 hour

    @classmethod
    def get_settings(cls) -> Settings:
        """Get cached settings or load from database."""
        settings = cache.get(cls.CACHE_KEY)
        if settings is None:
            settings = Settings.load()
            cache.set(cls.CACHE_KEY, settings, cls.CACHE_TIMEOUT)
        return settings  # type: ignore[no-any-return]

    @classmethod
    def get_currency(cls) -> str:
        """Get current currency code."""
        return cls.get_settings().currency

    @classmethod
    def get_locale(cls) -> str:
        """Get current locale."""
        return cls.get_settings().locale

    @classmethod
    def format_currency(
        cls, amount: Optional[Union[Decimal, float, int]], include_symbol: bool = True
    ) -> str:
        """
        Format amount as currency using current settings.

        Args:
            amount: Decimal or float amount to format
            include_symbol: Whether to include currency symbol

        Returns:
            Formatted currency string
        """
        if amount is None:
            return ""

        settings = cls.get_settings()

        # Ensure amount is Decimal
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        # Format using babel
        try:
            formatted = babel_format_currency(
                amount,
                settings.currency,
                locale=settings.locale,
                format_type="standard" if include_symbol else "accounting",
            )
            return formatted
        except Exception as e:
            # Fallback to basic formatting if babel fails
            return f"{settings.currency} {amount:.2f}"

    @classmethod
    def clear_cache(cls) -> None:
        """Clear settings cache."""
        cache.delete(cls.CACHE_KEY)
