from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from datetime import date, datetime
from collections import OrderedDict
from ..models import ExpenseItem, BudgetMonth, Budget, Expense, Payment
from ..forms import QuickExpenseForm
from ..services import SettingsService


def dashboard(request, budget_id):
    """Display most recent active month summary with pending and paid payments for a specific budget"""
    import calendar

    budget = get_object_or_404(Budget, id=budget_id)
    current_date = date.today()

    # Handle quick expense form submission
    if request.method == "POST":
        return handle_quick_expense(request, budget_id)

    # Initialize quick expense form for GET requests
    quick_expense_form = QuickExpenseForm()

    # Check if any months exist in the budget
    has_any_months = BudgetMonth.objects.filter(budget=budget).exists()

    # Get the most recent month from database for this budget
    current_month = (
        BudgetMonth.objects.filter(budget=budget).order_by("-year", "-month").first()
    )

    if current_month:
        # Get all expense items for the current month, ordered by due date
        current_month_items = (
            ExpenseItem.objects.filter(month=current_month)
            .select_related("expense", "expense__payee")
            .order_by("due_date")
        )

        # Get all pending expense items from past months
        all_past_items = (
            ExpenseItem.objects.filter(
                Q(month__budget=budget, month__year__lt=current_month.year)
                | Q(
                    month__budget=budget,
                    month__year=current_month.year,
                    month__month__lt=current_month.month,
                )
            )
            .select_related("expense", "expense__payee", "month")
            .order_by("-month__year", "-month__month", "due_date")
        )
        # Filter to only pending items using property
        past_pending_items = [
            item for item in all_past_items if item.status == ExpenseItem.STATUS_PENDING
        ]

        # Group all items by month for display with totals
        grouped_expense_items = OrderedDict()
        month_totals = {}

        # Add current month items first (newest)
        if current_month_items:
            current_month_key = f"{current_month.year}-{current_month.month:02d}"
            grouped_expense_items[current_month_key] = list(current_month_items)
            month_totals[current_month_key] = sum(
                item.get_remaining_amount() for item in current_month_items
            )

        # Add past months with pending items (already ordered by year/month desc)
        for item in past_pending_items:
            month_key = f"{item.month.year}-{item.month.month:02d}"
            if month_key not in grouped_expense_items:
                grouped_expense_items[month_key] = []
                month_totals[month_key] = 0
            grouped_expense_items[month_key].append(item)
            month_totals[month_key] += item.get_remaining_amount()

        # Keep as QuerySet for backward compatibility with template
        all_expense_items = current_month_items

        # Separate current month items for counting and totals
        pending_items = [
            item
            for item in current_month_items
            if item.status == ExpenseItem.STATUS_PENDING
        ]
        paid_items = [
            item
            for item in current_month_items
            if item.status == ExpenseItem.STATUS_PAID
        ]

        total_pending = sum(item.get_remaining_amount() for item in pending_items)
        total_paid = sum(item.get_remaining_amount() for item in paid_items)
        total_month = total_pending + total_paid

        # Calendar data
        # Get days with unpaid items in current month
        all_current_items = current_month.expenseitem_set.filter(due_date__isnull=False)
        unpaid_days = [
            item.due_date.day
            for item in all_current_items
            if item.due_date and item.status == ExpenseItem.STATUS_PENDING
        ]
        due_days = set(unpaid_days)

        # Check if any overdue items exist from previous months in this budget
        has_overdue = len(past_pending_items) > 0

        # Add today to due_days if there are overdue items and we're showing current calendar month
        if (
            has_overdue
            and current_date.month == current_month.month
            and current_date.year == current_month.year
        ):
            due_days.add(current_date.day)
    else:
        # No months exist in the system
        all_expense_items = ExpenseItem.objects.none()
        pending_items = []
        paid_items = []
        total_pending = 0
        total_paid = 0
        total_month = 0
        due_days = set()
        grouped_expense_items = OrderedDict()
        month_totals = {}

    # Build calendar weeks (Monday start) - show most recent month if available
    calendar.setfirstweekday(calendar.MONDAY)
    if current_month:
        cal = calendar.monthcalendar(current_month.year, current_month.month)
        display_year = current_month.year
        display_month = current_month.month
    else:
        # Fallback to current calendar month if no months exist
        cal = calendar.monthcalendar(current_date.year, current_date.month)
        display_year = current_date.year
        display_month = current_date.month

    # Create normalized summary data for the include
    dashboard_summary = {
        "total": total_month,
        "paid": total_paid,
        "pending": total_pending,
        "paid_count": len(paid_items),
        "pending_count": len(pending_items),
    }

    # Get current weekday (0=Monday, 6=Sunday)
    current_weekday = current_date.weekday()

    # Calculate relative time indicator for dashboard title
    relative_time_text = ""
    if (
        current_month
        and hasattr(current_month, "year")
        and hasattr(current_month, "month")
    ):
        try:
            current_month_date = date(current_month.year, current_month.month, 1)
            current_calendar_date = date(current_date.year, current_date.month, 1)

            if current_month_date < current_calendar_date:
                # Calculate months difference using built-in datetime
                months_ago = (
                    current_calendar_date.year - current_month_date.year
                ) * 12 + (current_calendar_date.month - current_month_date.month)

                if months_ago == 1:
                    relative_time_text = " (1 month ago)"
                else:
                    relative_time_text = f" ({months_ago} months ago)"
        except (TypeError, AttributeError):
            # Handle cases where mocks or invalid data are used (e.g., in tests)
            relative_time_text = ""

    context = {
        "budget": budget,
        "current_month": current_month,
        "current_date": current_date,
        "has_any_months": has_any_months,
        "all_expense_items": all_expense_items,
        "grouped_expense_items": grouped_expense_items,
        "month_totals": month_totals,
        "dashboard_summary": dashboard_summary,
        "not_has_any_months": not has_any_months,
        "not_current_month": current_month is None,
        # Calendar context
        "calendar_weeks": cal,
        "due_days": due_days,
        "today": current_date,
        "month_name": calendar.month_name[display_month],
        "year": display_year,
        "current_weekday": current_weekday,
        # Display month context for proper date highlighting
        "display_month": display_month,
        "display_year": display_year,
        # Relative time context
        "relative_time_text": relative_time_text,
        # Quick expense form
        "quick_expense_form": quick_expense_form,
    }
    return render(request, "expenses/dashboard.html", context)


def handle_quick_expense(request, budget_id):
    """Handle quick expense form submission"""
    budget = get_object_or_404(Budget, id=budget_id)
    form = QuickExpenseForm(request.POST)

    if form.is_valid():
        try:
            with transaction.atomic():
                # Get or create current month
                current_date = date.today()
                current_month, created = BudgetMonth.objects.get_or_create(
                    budget=budget,
                    year=current_date.year,
                    month=current_date.month,
                    defaults={"initial_amount": budget.initial_amount},
                )

                # Create one-time expense
                expense = Expense.objects.create(
                    budget=budget,
                    payee=form.cleaned_data["payee"],
                    title=form.cleaned_data["title"],
                    expense_type=Expense.TYPE_ONE_TIME,
                    amount=form.cleaned_data["amount"],
                    start_date=current_date,
                    day_of_month=current_date.day,
                )

                # Create expense item
                expense_item = ExpenseItem.objects.create(
                    expense=expense,
                    month=current_month,
                    due_date=current_date,
                    amount=form.cleaned_data["amount"],
                )

                # Create payment if requested
                if form.cleaned_data["mark_as_paid"]:
                    Payment.objects.create(
                        expense_item=expense_item,
                        amount=form.cleaned_data["amount"],
                        payment_date=datetime.now(),
                    )
                    # Check if expense should be completed
                    from ..services import check_expense_completion

                    check_expense_completion(expense)

                    formatted_amount = SettingsService.format_currency(expense.amount)
                    messages.success(
                        request,
                        f'Quick expense "{expense.title}" ({formatted_amount}) created and marked as paid!',
                    )
                else:
                    formatted_amount = SettingsService.format_currency(expense.amount)
                    messages.success(
                        request,
                        f'Quick expense "{expense.title}" ({formatted_amount}) created successfully!',
                    )

        except Exception as e:
            messages.error(request, f"Error creating expense: {str(e)}")
    else:
        # Form validation errors
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field.title()}: {error}")
        messages.error(request, f"Form errors: {'; '.join(error_messages)}")

    return redirect("dashboard", budget_id=budget_id)
