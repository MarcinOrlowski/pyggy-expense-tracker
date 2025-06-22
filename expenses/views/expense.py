from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import date
from collections import OrderedDict
from typing import List
from ..models import Expense, ExpenseItem, BudgetMonth, Payee, Budget
from ..forms import ExpenseForm


def expense_list(request, budget_id):
    """List active expenses with filtering options for a specific budget"""
    budget = get_object_or_404(Budget, id=budget_id)

    # Get expenses that belong directly to this budget, ordered by start_date desc
    expenses = (
        Expense.objects.filter(closed_at__isnull=True, budget=budget)
        .select_related("payee")
        .order_by("-start_date", "-created_at")
    )

    # Simple filtering
    expense_type = request.GET.get("type")
    payee_id = request.GET.get("payee")

    if expense_type:
        expenses = expenses.filter(expense_type=expense_type)
    if payee_id:
        expenses = expenses.filter(payee_id=payee_id)

    # Group expenses by year-month
    grouped_expenses: OrderedDict[str, List[Expense]] = OrderedDict()
    for expense in expenses:
        year_month = expense.start_date.strftime("%Y-%m")
        if year_month not in grouped_expenses:
            grouped_expenses[year_month] = []
        grouped_expenses[year_month].append(expense)

    # Only show non-hidden payees in the filter dropdown
    payees = Payee.objects.filter(hidden_at__isnull=True)

    context = {
        "budget": budget,
        "expenses": expenses,
        "grouped_expenses": grouped_expenses,
        "payees": payees,
        "expense_types": Expense.EXPENSE_TYPES,
        "selected_type": expense_type,
        "selected_payee": int(payee_id) if payee_id else None,
    }
    return render(request, "expenses/expense_list.html", context)


def expense_create(request, budget_id):
    """Create new expense with form validation"""
    budget = get_object_or_404(Budget, id=budget_id)

    if request.method == "POST":
        form = ExpenseForm(request.POST, budget=budget)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.budget = budget
            expense.save()
            # Handle expense items creation if it starts in current month
            from ..services import handle_new_expense

            handle_new_expense(expense, budget)
            messages.success(
                request, f'Expense "{expense.title}" created successfully.'
            )
            return redirect("expense_list", budget_id=budget_id)
    else:
        # Set default start date to current month's first day for this budget
        most_recent_month = (
            BudgetMonth.objects.filter(budget=budget)
            .order_by("-year", "-month")
            .first()
        )
        if most_recent_month:
            default_date = date(most_recent_month.year, most_recent_month.month, 1)
        else:
            default_date = date.today()

        form = ExpenseForm(
            initial={"started_at": default_date.strftime("%Y-%m-%d")}, budget=budget
        )

    context = {"budget": budget, "form": form, "title": "Create New Expense"}
    return render(request, "expenses/expense_form.html", context)


def expense_detail(request, budget_id, pk):
    """Display expense details and related items"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense = get_object_or_404(Expense, pk=pk, budget=budget)

    # Get all expense items for this expense
    expense_items = (
        ExpenseItem.objects.filter(expense=expense)
        .select_related("month")
        .order_by("due_date")
    )

    # Get edit restrictions for the template
    edit_restrictions = expense.get_edit_restrictions()

    context = {
        "budget": budget,
        "expense": expense,
        "expense_items": expense_items,
        "edit_restrictions": edit_restrictions,
    }
    return render(request, "expenses/expense_detail.html", context)


def expense_edit(request, budget_id, pk):
    """Edit existing expense"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense = get_object_or_404(Expense, pk=pk, budget=budget)

    # Check if expense can be edited
    if not expense.can_be_edited():
        restrictions = expense.get_edit_restrictions()
        reasons = restrictions["reasons"]
        reason_text = " ".join(reasons) if isinstance(reasons, list) else str(reasons)
        messages.error(request, f"This expense cannot be edited. {reason_text}")
        return redirect("expense_detail", budget_id=budget_id, pk=expense.pk)

    if request.method == "POST":
        original_start_date = expense.start_date
        form = ExpenseForm(request.POST, instance=expense, budget=budget)
        if form.is_valid():
            expense = form.save()
            # If start date changed and now starts in current month, handle expense items
            if original_start_date != expense.start_date:
                from ..services import handle_new_expense

                handle_new_expense(expense, budget)
            messages.success(
                request, f'Expense "{expense.title}" updated successfully.'
            )
            return redirect("expense_detail", budget_id=budget_id, pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense, budget=budget)

    # Get edit restrictions to pass to template
    restrictions = expense.get_edit_restrictions()

    context = {
        "budget": budget,
        "form": form,
        "expense": expense,
        "title": f"Edit Expense: {expense.title}",
        "edit_restrictions": restrictions,
    }
    return render(request, "expenses/expense_form.html", context)


def expense_delete(request, budget_id, pk):
    """Delete expense with confirmation"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense = get_object_or_404(Expense, pk=pk, budget=budget)

    if request.method == "POST":
        title = expense.title
        expense.delete()
        messages.success(request, f'Expense "{title}" deleted successfully.')
        return redirect("expense_list", budget_id=budget_id)

    context = {
        "budget": budget,
        "expense": expense,
    }
    return render(request, "expenses/expense_confirm_delete.html", context)
