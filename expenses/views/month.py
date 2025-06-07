from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models import BudgetMonth, ExpenseItem, Budget


def month_list(request, budget_id):
    """List all months for a specific budget"""
    budget = get_object_or_404(Budget, id=budget_id)
    months = BudgetMonth.objects.filter(budget=budget)

    # Calculate balance for each month (expenses as negative impact)
    from django.db.models import Sum
    from decimal import Decimal

    for month in months:
        # Sum all expense items for this month
        total_expenses = month.expenseitem_set.aggregate(total=Sum("amount"))[
            "total"
        ] or Decimal("0.00")

        # Balance shows financial impact (negative for expenses)
        month.balance = -total_expenses  # type: ignore[attr-defined]

    # Get next allowed month for this budget
    next_allowed = BudgetMonth.get_next_allowed_month(budget=budget)

    context = {
        "budget": budget,
        "months": months,
        "next_allowed_month": next_allowed,
    }
    return render(request, "expenses/month_list.html", context)


def month_detail(request, budget_id, year, month):
    """Display month details with expense items"""
    budget = get_object_or_404(Budget, id=budget_id)
    month_obj = get_object_or_404(BudgetMonth, year=year, month=month, budget=budget)
    expense_items = ExpenseItem.objects.filter(month=month_obj).select_related(
        "expense", "expense__payee"
    )

    total_amount = sum(item.get_remaining_amount() for item in expense_items)
    paid_amount = sum(item.get_remaining_amount() for item in expense_items if item.status == ExpenseItem.STATUS_PAID)
    pending_amount = sum(item.get_remaining_amount() for item in expense_items if item.status == ExpenseItem.STATUS_PENDING)

    # Create normalized summary data for the include
    month_summary = {
        "total": total_amount,
        "paid": paid_amount,
        "pending": pending_amount,
    }

    context = {
        "budget": budget,
        # Original context for backward compatibility
        "month": month_obj,
        "expense_items": expense_items,
        "total_amount": total_amount,
        "paid_amount": paid_amount,
        "pending_amount": pending_amount,
        # New normalized context for includes
        "month_summary": month_summary,
    }
    return render(request, "expenses/month_detail.html", context)


def month_delete(request, budget_id, year, month):
    """Delete month with validation"""
    budget = get_object_or_404(Budget, id=budget_id)
    month_obj = get_object_or_404(BudgetMonth, year=year, month=month, budget=budget)

    # Check if this is the most recent month for this budget
    most_recent = BudgetMonth.get_most_recent(budget=budget)
    if most_recent != month_obj:
        messages.error(request, "You can only delete the most recent month.")
        return redirect("month_list", budget_id=budget_id)

    # Check if month has paid expenses
    if month_obj.has_paid_expenses():
        messages.error(
            request,
            f"Cannot delete month {month_obj} because it contains paid expenses.",
        )
        return redirect("month_list", budget_id=budget_id)

    if request.method == "POST":
        month_str = str(month_obj)
        month_obj.delete()
        messages.success(request, f"Month {month_str} deleted successfully.")
        return redirect("month_list", budget_id=budget_id)

    # Count expense items that will be deleted
    expense_items_count = month_obj.expenseitem_set.count()

    context = {
        "budget": budget,
        "month": month_obj,
        "expense_items_count": expense_items_count,
    }
    return render(request, "expenses/month_confirm_delete.html", context)


def month_process(request, budget_id):
    """Process new month generation for a specific budget"""
    budget = get_object_or_404(Budget, id=budget_id)

    # Determine next month to create automatically
    next_allowed = BudgetMonth.get_next_allowed_month(budget=budget)

    if not next_allowed:
        # No months exist for this budget, use budget start_date for initial month
        start_date = budget.start_date
        year = start_date.year
        month = start_date.month
    else:
        # Use next allowed month
        year = next_allowed["year"]
        month = next_allowed["month"]

    try:
        from ..services import process_new_month

        month_obj = process_new_month(year, month, budget)
        if not next_allowed:
            messages.success(
                request,
                f"Initial month {month_obj} created successfully based on budget start date.",
            )
        else:
            messages.success(request, f"Next month {month_obj} added successfully.")
        return redirect("month_list", budget_id=budget_id)
    except Exception as e:
        messages.error(request, f"Error processing month: {str(e)}")
        return redirect("month_list", budget_id=budget_id)
