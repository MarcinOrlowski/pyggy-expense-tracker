from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import datetime
from ..models import ExpenseItem, Budget
from ..forms import PaymentForm, ExpenseItemEditForm


def expense_item_pay(request, budget_id, pk):
    """Record payment for expense item"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense_item = get_object_or_404(ExpenseItem, pk=pk, month__budget=budget)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=expense_item)
        if form.is_valid():
            item = form.save()
            if item.status == 'paid':
                # Check if expense should be completed
                from ..services import check_expense_completion
                check_expense_completion(item.expense)
            messages.success(request, 'Payment recorded successfully.')
            return redirect('expense_detail', budget_id=budget_id, pk=expense_item.expense.pk)
    else:
        form = PaymentForm(instance=expense_item, initial={
            'payment_date': datetime.now().strftime('%Y-%m-%dT%H:%M'),
            'status': 'paid'
        })
    
    context = {
        'budget': budget,
        'form': form,
        'expense_item': expense_item,
        'title': f'Record Payment: {expense_item.expense.title}'
    }
    return render(request, 'expenses/payment_form.html', context)


def expense_item_unpay(request, budget_id, pk):
    """Mark expense item as unpaid"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense_item = get_object_or_404(ExpenseItem, pk=pk, month__budget=budget)
    
    if request.method == 'POST':
        expense_item.status = 'pending'
        expense_item.payment_date = None
        expense_item.payment_method = None
        expense_item.save()
        messages.success(request, 'Payment unmarked successfully.')
        return redirect('expense_detail', budget_id=budget_id, pk=expense_item.expense.pk)
    
    context = {
        'budget': budget,
        'expense_item': expense_item,
    }
    return render(request, 'expenses/expense_item_confirm_unpay.html', context)


def expense_item_edit(request, budget_id, pk):
    """Edit expense item due date with month validation"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense_item = get_object_or_404(ExpenseItem, pk=pk, month__budget=budget)
    
    if request.method == 'POST':
        form = ExpenseItemEditForm(request.POST, instance=expense_item)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Due date for "{item.expense.title}" updated successfully.')
            return redirect('dashboard', budget_id=budget_id)
    else:
        form = ExpenseItemEditForm(instance=expense_item)
    
    context = {
        'budget': budget,
        'form': form,
        'expense_item': expense_item,
        'title': f'Edit Due Date: {expense_item.expense.title}'
    }
    return render(request, 'expenses/expense_item_edit.html', context)