from django.shortcuts import render, get_object_or_404
from datetime import date
from ..models import ExpenseItem, Month, Budget


def dashboard(request, budget_id):
    """Display most recent active month summary with pending and paid payments for a specific budget"""
    import calendar

    budget = get_object_or_404(Budget, id=budget_id)
    current_date = date.today()

    # Check if any months exist in the budget
    has_any_months = Month.objects.filter(budget=budget).exists()

    # Get the most recent month from database for this budget
    current_month = (
        Month.objects.filter(budget=budget).order_by("-year", "-month").first()
    )

    if current_month:
        # Get all expense items for the current month, ordered by due date
        all_expense_items = (
            ExpenseItem.objects.filter(month=current_month)
            .select_related("expense", "expense__payee")
            .order_by("due_date")
        )

        # Separate for counting and totals
        pending_items = [item for item in all_expense_items if item.status == "pending"]
        paid_items = [item for item in all_expense_items if item.status == "paid"]

        total_pending = sum(item.amount for item in pending_items)
        total_paid = sum(item.amount for item in paid_items)
        total_month = total_pending + total_paid

        # Calendar data
        # Get days with unpaid items in current month
        due_days = set(
            current_month.expenseitem_set.filter(
                payment_date__isnull=True, due_date__isnull=False
            ).values_list("due_date__day", flat=True)
        )

        # Check if any overdue items exist from previous months in this budget
        has_overdue = (
            ExpenseItem.objects.filter(
                payment_date__isnull=True,
                due_date__lt=current_date,
                month__budget=budget,
            )
            .exclude(month=current_month)
            .exists()
        )

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

    context = {
        "budget": budget,
        "current_month": current_month,
        "current_date": current_date,
        "has_any_months": has_any_months,
        "all_expense_items": all_expense_items,
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
    }
    return render(request, "expenses/dashboard.html", context)
