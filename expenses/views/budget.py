from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import date
from ..models import Budget
from ..forms import BudgetForm


def budget_list(request):
    """List all budgets with current balance calculations"""
    budgets = list(Budget.objects.all())

    # Add balance calculation for each budget
    for budget in budgets:
        budget.current_balance = budget.get_current_balance()  # type: ignore[attr-defined]

    context = {
        "budgets": budgets,
    }
    return render(request, "expenses/budget_list.html", context)


def budget_create(request):
    """Create new budget"""
    if request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save()
            messages.success(request, f'Budget "{budget.name}" created successfully.')
            return redirect("budget_list")
    else:
        form = BudgetForm(initial={"start_date": date.today().strftime("%Y-%m-%d")})

    context = {"form": form, "title": "Create New Budget"}
    return render(request, "expenses/budget_form.html", context)


def budget_edit(request, pk):
    """Edit existing budget"""
    budget = get_object_or_404(Budget, pk=pk)

    if request.method == "POST":
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            budget = form.save()
            messages.success(request, f'Budget "{budget.name}" updated successfully.')
            return redirect("budget_list")
    else:
        form = BudgetForm(instance=budget)

    context = {"form": form, "budget": budget, "title": f"Edit Budget: {budget.name}"}
    return render(request, "expenses/budget_form.html", context)


def budget_delete(request, pk):
    """Delete budget with confirmation"""
    budget = get_object_or_404(Budget, pk=pk)

    # Check if budget has associated months
    month_count = budget.month_set.count()

    if request.method == "POST":
        if month_count > 0:
            messages.error(
                request,
                f'Cannot delete budget "{budget.name}" because it has {month_count} associated months.',
            )
        else:
            name = budget.name
            budget.delete()
            messages.success(request, f'Budget "{name}" deleted successfully.')
        return redirect("budget_list")

    context = {
        "budget": budget,
        "month_count": month_count,
    }
    return render(request, "expenses/budget_confirm_delete.html", context)
