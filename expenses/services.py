from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from datetime import date, datetime
from typing import List
from .models import Expense, ExpenseItem, Month


def process_new_month(year: int, month: int) -> Month:
    """
    Create new month and generate expense items for active expenses.

    Args:
        year: Target year (2020-2099)
        month: Target month (1-12)

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
            year=year,
            month=month
        )

        if created:
            # Generate expense items for all active expenses
            active_expenses = Expense.objects.filter(closed_at__isnull=True)

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
    """
    items = []
    expense_start_date = expense.started_at

    # Check if the expense has started by this month
    # For the start month, we create items even if the start date is mid-month
    import calendar
    last_day = calendar.monthrange(month.year, month.month)[1]
    month_end_date = date(month.year, month.month, last_day)

    if expense_start_date > month_end_date:
        return items

    if expense.expense_type == 'endless_recurring':
        # Create one item per month
        try:
            # Handle case where start day doesn't exist in target month (e.g., Feb 30)
            due_date = date(month.year, month.month, expense_start_date.day)
        except ValueError:
            # Use last day of month if start day doesn't exist
            import calendar
            last_day = calendar.monthrange(month.year, month.month)[1]
            due_date = date(month.year, month.month, last_day)

        item = ExpenseItem.objects.create(
            expense=expense,
            month=month,
            due_date=due_date,
            amount=expense.total_amount
        )
        items.append(item)

    elif expense.expense_type == 'split_payment':
        # Check how many items we've already created
        existing_count = ExpenseItem.objects.filter(expense=expense).count()

        if existing_count < expense.installments_count:
            due_date = date(month.year, month.month, expense_start_date.day)
            try:
                due_date = date(month.year, month.month, expense_start_date.day)
            except ValueError:
                import calendar
                last_day = calendar.monthrange(month.year, month.month)[1]
                due_date = date(month.year, month.month, last_day)

            installment_amount = calculate_installment_amount(expense)

            item = ExpenseItem.objects.create(
                expense=expense,
                month=month,
                due_date=due_date,
                amount=installment_amount
            )
            items.append(item)

    elif expense.expense_type == 'one_time':
        # Only create if this is the start month and no items exist yet
        start_month_date = date(expense_start_date.year, expense_start_date.month, 1)
        target_month_date = date(month.year, month.month, 1)

        if (start_month_date == target_month_date and
                not ExpenseItem.objects.filter(expense=expense).exists()):
            item = ExpenseItem.objects.create(
                expense=expense,
                month=month,
                due_date=expense_start_date,
                amount=expense.total_amount
            )
            items.append(item)

    return items


def calculate_installment_amount(expense: Expense) -> Decimal:
    """Calculate per-installment amount for split payments."""
    if expense.expense_type != 'split_payment' or expense.installments_count <= 0:
        raise ValueError("Can only calculate installments for split payment expenses")

    return expense.total_amount / expense.installments_count


def check_expense_completion(expense: Expense) -> bool:
    """
    Check if expense should be marked as complete.

    Rules:
    - one_time: Complete when single item is paid
    - split_payment: Complete when all installments paid
    - endless_recurring: Manual completion only
    """
    if expense.closed_at:
        return True  # Already completed

    if expense.expense_type == 'one_time':
        # Complete when the single item is paid
        paid_items = ExpenseItem.objects.filter(expense=expense, status='paid').count()
        if paid_items > 0:
            expense.closed_at = timezone.now()
            expense.save()
            return True

    elif expense.expense_type == 'split_payment':
        # Complete when all installments are paid
        paid_items = ExpenseItem.objects.filter(expense=expense, status='paid').count()
        if paid_items >= expense.installments_count:
            expense.closed_at = timezone.now()
            expense.save()
            return True

    # endless_recurring expenses are only manually completed
    return False


def handle_new_expense(expense: Expense) -> None:
    """
    Handle newly created expense - create expense items if it starts in current month.
    
    Args:
        expense: The newly created expense
    """
    most_recent_month = Month.get_most_recent()
    if not most_recent_month:
        return  # No months exist yet
    
    # Check if expense starts in the current month
    expense_start_date = expense.started_at
    current_month_start = date(most_recent_month.year, most_recent_month.month, 1)
    
    import calendar
    last_day = calendar.monthrange(most_recent_month.year, most_recent_month.month)[1]
    current_month_end = date(most_recent_month.year, most_recent_month.month, last_day)
    
    # If expense starts within the current month, create expense items immediately
    if current_month_start <= expense_start_date <= current_month_end:
        create_expense_items_for_month(expense, most_recent_month)
