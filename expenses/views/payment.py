from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import datetime
from ..models import ExpenseItem, Budget, Payment
from ..forms import PaymentForm, ExpenseItemEditForm


def expense_item_pay(request, budget_id, pk):
    """Record payment for expense item"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense_item = get_object_or_404(ExpenseItem, pk=pk, month__budget=budget)

    if request.method == "POST":
        form = PaymentForm(request.POST, expense_item=expense_item)
        if form.is_valid():
            payment = form.save()
            # Check if expense should be completed
            from ..services import check_expense_completion
            check_expense_completion(expense_item.expense)
            
            remaining = expense_item.get_remaining_amount()
            if remaining <= 0:
                messages.success(request, f"Payment of {payment.amount} recorded. Expense is now fully paid!")
            else:
                messages.success(request, f"Payment of {payment.amount} recorded. Remaining balance: {remaining}")
            return redirect("dashboard", budget_id=budget_id)
    else:
        form = PaymentForm(
            expense_item=expense_item,
            initial={
                "payment_date": datetime.now().strftime("%Y-%m-%dT%H:%M"),
            },
        )

    context = {
        "budget": budget,
        "form": form,
        "expense_item": expense_item,
        "title": f"Record Payment: {expense_item.expense.title}",
    }
    return render(request, "expenses/payment_form.html", context)


def expense_item_unpay(request, budget_id, pk):
    """Mark expense item as unpaid by removing all payments"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense_item = get_object_or_404(ExpenseItem, pk=pk, month__budget=budget)

    if request.method == "POST":
        payment_count = expense_item.payment_set.count()
        expense_item.payment_set.all().delete()
        messages.success(request, f"All payments ({payment_count}) removed successfully.")
        return redirect("dashboard", budget_id=budget_id)

    context = {
        "budget": budget,
        "expense_item": expense_item,
    }
    return render(request, "expenses/expense_item_confirm_unpay.html", context)


def expense_item_edit(request, budget_id, pk):
    """Edit expense item due date with month validation"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense_item = get_object_or_404(ExpenseItem, pk=pk, month__budget=budget)

    if request.method == "POST":
        form = ExpenseItemEditForm(request.POST, instance=expense_item)
        if form.is_valid():
            item = form.save()
            messages.success(
                request, f'Due date for "{item.expense.title}" updated successfully.'
            )
            return redirect("dashboard", budget_id=budget_id)
    else:
        form = ExpenseItemEditForm(instance=expense_item)

    context = {
        "budget": budget,
        "form": form,
        "expense_item": expense_item,
        "title": f"Edit Due Date: {expense_item.expense.title}",
    }
    return render(request, "expenses/expense_item_edit.html", context)


def expense_item_payments(request, budget_id, pk):
    """List all payments for a specific expense item"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense_item = get_object_or_404(ExpenseItem, pk=pk, month__budget=budget)
    
    # Get all payments for this expense item, ordered by payment date
    payments = expense_item.payment_set.select_related("payment_method").order_by("-payment_date")
    
    context = {
        "budget": budget,
        "expense_item": expense_item,
        "payments": payments,
        "title": f"Payments: {expense_item.expense.title}",
    }
    return render(request, "expenses/expense_item_payments.html", context)
