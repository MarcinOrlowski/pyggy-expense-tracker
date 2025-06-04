from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date
from .models import Expense, ExpenseItem, Month, Payee, PaymentMethod, Budget
from .forms import ExpenseForm, PaymentForm, PayeeForm, BudgetForm, ExpenseItemEditForm


def dashboard(request, budget_id):
    """Display most recent active month summary with pending and paid payments for a specific budget"""
    import calendar
    
    budget = get_object_or_404(Budget, id=budget_id)
    current_date = date.today()
    
    # Check if any months exist in the budget
    has_any_months = Month.objects.filter(budget=budget).exists()
    
    # Get the most recent month from database for this budget
    current_month = Month.objects.filter(budget=budget).order_by('-year', '-month').first()
    
    if current_month:
        # Get all expense items for the current month, ordered by due date
        all_expense_items = ExpenseItem.objects.filter(
            month=current_month
        ).select_related('expense', 'expense__payee').order_by('due_date')
        
        # Separate for counting and totals
        pending_items = [item for item in all_expense_items if item.status == 'pending']
        paid_items = [item for item in all_expense_items if item.status == 'paid']
        
        total_pending = sum(item.amount for item in pending_items)
        total_paid = sum(item.amount for item in paid_items)
        total_month = total_pending + total_paid
        
        # Calendar data
        # Get days with unpaid items in current month
        due_days = set(
            current_month.expenseitem_set.filter(
                payment_date__isnull=True,
                due_date__isnull=False
            ).values_list('due_date__day', flat=True)
        )
        
        # Check if any overdue items exist from previous months in this budget
        has_overdue = ExpenseItem.objects.filter(
            payment_date__isnull=True,
            due_date__lt=current_date,
            month__budget=budget
        ).exclude(
            month=current_month
        ).exists()
        
        # Add today to due_days if there are overdue items and we're showing current calendar month
        if has_overdue and current_date.month == current_month.month and current_date.year == current_month.year:
            due_days.add(current_date.day)
    else:
        # No months exist in the system
        all_expense_items = []
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
        'total': total_month,
        'paid': total_paid,
        'pending': total_pending,
        'paid_count': len(paid_items),
        'pending_count': len(pending_items),
    }
    
    # Get current weekday (0=Monday, 6=Sunday)
    current_weekday = current_date.weekday()
    
    context = {
        'budget': budget,
        'current_month': current_month,
        'current_date': current_date,
        'has_any_months': has_any_months,
        'all_expense_items': all_expense_items,
        'dashboard_summary': dashboard_summary,
        'not_has_any_months': not has_any_months,
        'not_current_month': current_month is None,
        # Calendar context
        'calendar_weeks': cal,
        'due_days': due_days,
        'today': current_date,
        'month_name': calendar.month_name[display_month],
        'year': display_year,
        'current_weekday': current_weekday,
    }
    return render(request, 'expenses/dashboard.html', context)


def expense_list(request, budget_id):
    """List active expenses with filtering options for a specific budget"""
    budget = get_object_or_404(Budget, id=budget_id)
    
    # Get expenses that belong directly to this budget
    expenses = Expense.objects.filter(
        closed_at__isnull=True,
        budget=budget
    ).select_related('payee')
    
    # Simple filtering
    expense_type = request.GET.get('type')
    payee_id = request.GET.get('payee')
    
    if expense_type:
        expenses = expenses.filter(expense_type=expense_type)
    if payee_id:
        expenses = expenses.filter(payee_id=payee_id)
    
    # Only show non-hidden payees in the filter dropdown
    payees = Payee.objects.filter(hidden_at__isnull=True)
    
    context = {
        'budget': budget,
        'expenses': expenses,
        'payees': payees,
        'expense_types': Expense.EXPENSE_TYPES,
        'selected_type': expense_type,
        'selected_payee': int(payee_id) if payee_id else None,
    }
    return render(request, 'expenses/expense_list.html', context)


def expense_create(request, budget_id):
    """Create new expense with form validation"""
    budget = get_object_or_404(Budget, id=budget_id)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, budget=budget)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.budget = budget
            expense.save()
            # Handle expense items creation if it starts in current month
            from .services import handle_new_expense
            handle_new_expense(expense, budget)
            messages.success(request, f'Expense "{expense.title}" created successfully.')
            return redirect('expense_detail', budget_id=budget_id, pk=expense.pk)
    else:
        # Set default start date to current month's first day for this budget
        most_recent_month = Month.objects.filter(budget=budget).order_by('-year', '-month').first()
        if most_recent_month:
            default_date = date(most_recent_month.year, most_recent_month.month, 1)
        else:
            default_date = date.today()
        
        form = ExpenseForm(initial={
            'started_at': default_date.strftime('%Y-%m-%d')
        }, budget=budget)
    
    context = {
        'budget': budget,
        'form': form,
        'title': 'Create New Expense'
    }
    return render(request, 'expenses/expense_form.html', context)


def expense_detail(request, budget_id, pk):
    """Display expense details and related items"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense = get_object_or_404(Expense, pk=pk, budget=budget)
    
    # Get all expense items for this expense
    expense_items = ExpenseItem.objects.filter(
        expense=expense
    ).select_related('month', 'payment_method').order_by('due_date')
    
    # Get edit restrictions for the template
    edit_restrictions = expense.get_edit_restrictions()
    
    context = {
        'budget': budget,
        'expense': expense,
        'expense_items': expense_items,
        'edit_restrictions': edit_restrictions,
    }
    return render(request, 'expenses/expense_detail.html', context)


def expense_edit(request, budget_id, pk):
    """Edit existing expense"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense = get_object_or_404(Expense, pk=pk, budget=budget)
    
    # Check if expense can be edited
    if not expense.can_be_edited():
        restrictions = expense.get_edit_restrictions()
        messages.error(request, f'This expense cannot be edited. {" ".join(restrictions["reasons"])}')
        return redirect('expense_detail', budget_id=budget_id, pk=expense.pk)
    
    if request.method == 'POST':
        original_start_date = expense.start_date
        form = ExpenseForm(request.POST, instance=expense, budget=budget)
        if form.is_valid():
            expense = form.save()
            # If start date changed and now starts in current month, handle expense items
            if original_start_date != expense.start_date:
                from .services import handle_new_expense
                handle_new_expense(expense, budget)
            messages.success(request, f'Expense "{expense.title}" updated successfully.')
            return redirect('expense_detail', budget_id=budget_id, pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense, budget=budget)
    
    # Get edit restrictions to pass to template
    restrictions = expense.get_edit_restrictions()
    
    context = {
        'budget': budget,
        'form': form,
        'expense': expense,
        'title': f'Edit Expense: {expense.title}',
        'edit_restrictions': restrictions
    }
    return render(request, 'expenses/expense_form.html', context)


def expense_delete(request, budget_id, pk):
    """Delete expense with confirmation"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense = get_object_or_404(Expense, pk=pk, budget=budget)
    
    if request.method == 'POST':
        title = expense.title
        expense.delete()
        messages.success(request, f'Expense "{title}" deleted successfully.')
        return redirect('expense_list', budget_id=budget_id)
    
    context = {
        'budget': budget,
        'expense': expense,
    }
    return render(request, 'expenses/expense_confirm_delete.html', context)


def month_list(request, budget_id):
    """List all months for a specific budget"""
    budget = get_object_or_404(Budget, id=budget_id)
    months = Month.objects.filter(budget=budget)
    
    # Get next allowed month for this budget
    next_allowed = Month.get_next_allowed_month(budget=budget)
    
    context = {
        'budget': budget,
        'months': months,
        'next_allowed_month': next_allowed,
    }
    return render(request, 'expenses/month_list.html', context)


def month_detail(request, budget_id, year, month):
    """Display month details with expense items"""
    budget = get_object_or_404(Budget, id=budget_id)
    month_obj = get_object_or_404(Month, year=year, month=month, budget=budget)
    expense_items = ExpenseItem.objects.filter(
        month=month_obj
    ).select_related('expense', 'expense__payee', 'payment_method')
    
    total_amount = sum(item.amount for item in expense_items)
    paid_amount = sum(item.amount for item in expense_items if item.status == 'paid')
    pending_amount = total_amount - paid_amount
    
    # Create normalized summary data for the include
    month_summary = {
        'total': total_amount,
        'paid': paid_amount,
        'pending': pending_amount,
    }
    
    context = {
        'budget': budget,
        # Original context for backward compatibility
        'month': month_obj,
        'expense_items': expense_items,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'pending_amount': pending_amount,
        # New normalized context for includes
        'month_summary': month_summary,
    }
    return render(request, 'expenses/month_detail.html', context)


def month_delete(request, budget_id, year, month):
    """Delete month with validation"""
    budget = get_object_or_404(Budget, id=budget_id)
    month_obj = get_object_or_404(Month, year=year, month=month, budget=budget)
    
    # Check if this is the most recent month for this budget
    most_recent = Month.get_most_recent(budget=budget)
    if most_recent != month_obj:
        messages.error(request, 'You can only delete the most recent month.')
        return redirect('month_list', budget_id=budget_id)
    
    # Check if month has paid expenses
    if month_obj.has_paid_expenses():
        messages.error(request, f'Cannot delete month {month_obj} because it contains paid expenses.')
        return redirect('month_list', budget_id=budget_id)
    
    if request.method == 'POST':
        month_str = str(month_obj)
        month_obj.delete()
        messages.success(request, f'Month {month_str} deleted successfully.')
        return redirect('month_list', budget_id=budget_id)
    
    # Count expense items that will be deleted
    expense_items_count = month_obj.expenseitem_set.count()
    
    context = {
        'budget': budget,
        'month': month_obj,
        'expense_items_count': expense_items_count,
    }
    return render(request, 'expenses/month_confirm_delete.html', context)


def month_process(request, budget_id):
    """Process new month generation for a specific budget"""
    budget = get_object_or_404(Budget, id=budget_id)
    
    # Determine next month to create automatically
    next_allowed = Month.get_next_allowed_month(budget=budget)
    
    if not next_allowed:
        # No months exist for this budget, use budget start_date for initial month
        start_date = budget.start_date
        year = start_date.year
        month = start_date.month
    else:
        # Use next allowed month
        year = next_allowed['year']
        month = next_allowed['month']
    
    try:
        from .services import process_new_month
        month_obj = process_new_month(year, month, budget)
        if not next_allowed:
            messages.success(request, f'Initial month {month_obj} created successfully based on budget start date.')
        else:
            messages.success(request, f'Next month {month_obj} added successfully.')
        return redirect('month_list', budget_id=budget_id)
    except Exception as e:
        messages.error(request, f'Error processing month: {str(e)}')
        return redirect('month_list', budget_id=budget_id)


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
                from .services import check_expense_completion
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


def payee_list(request):
    """List all payees"""
    show_hidden = request.GET.get('show_hidden', 'false') == 'true'
    
    if show_hidden:
        payees = Payee.objects.all()
    else:
        payees = Payee.objects.filter(hidden_at__isnull=True)
    
    # Add expense count for each payee
    for payee in payees:
        payee.expense_count = Expense.objects.filter(payee=payee).count()
    
    context = {
        'payees': payees,
        'show_hidden': show_hidden,
    }
    return render(request, 'expenses/payee_list.html', context)


def payee_create(request):
    """Create new payee"""
    if request.method == 'POST':
        form = PayeeForm(request.POST)
        if form.is_valid():
            payee = form.save()
            messages.success(request, f'Payee "{payee.name}" created successfully.')
            return redirect('payee_list')
    else:
        form = PayeeForm()
    
    context = {
        'form': form,
        'title': 'Create New Payee'
    }
    return render(request, 'expenses/payee_form.html', context)


def payee_edit(request, pk):
    """Edit existing payee"""
    payee = get_object_or_404(Payee, pk=pk)
    
    if request.method == 'POST':
        form = PayeeForm(request.POST, instance=payee)
        if form.is_valid():
            payee = form.save()
            messages.success(request, f'Payee "{payee.name}" updated successfully.')
            return redirect('payee_list')
    else:
        form = PayeeForm(instance=payee)
    
    context = {
        'form': form,
        'payee': payee,
        'title': f'Edit Payee: {payee.name}'
    }
    return render(request, 'expenses/payee_form.html', context)


def payee_delete(request, pk):
    """Delete payee with confirmation"""
    payee = get_object_or_404(Payee, pk=pk)
    
    # Check if payee has associated expenses
    expense_count = Expense.objects.filter(payee=payee).count()
    
    if request.method == 'POST':
        if expense_count > 0:
            messages.error(request, f'Cannot delete payee "{payee.name}" because it has {expense_count} associated expenses.')
        else:
            name = payee.name
            payee.delete()
            messages.success(request, f'Payee "{name}" deleted successfully.')
        return redirect('payee_list')
    
    context = {
        'payee': payee,
        'expense_count': expense_count,
    }
    return render(request, 'expenses/payee_confirm_delete.html', context)


def payee_hide(request, pk):
    """Hide a payee"""
    payee = get_object_or_404(Payee, pk=pk)
    
    if request.method == 'POST':
        payee.hidden_at = timezone.now()
        payee.save()
        messages.success(request, f'Payee "{payee.name}" has been hidden.')
        return redirect('payee_list')
    
    return redirect('payee_list')


def payee_unhide(request, pk):
    """Unhide a payee"""
    payee = get_object_or_404(Payee, pk=pk)
    
    if request.method == 'POST':
        payee.hidden_at = None
        payee.save()
        messages.success(request, f'Payee "{payee.name}" has been unhidden.')
        return redirect('payee_list')
    
    return redirect('payee_list')


def payment_method_list(request):
    """List all payment methods"""
    payment_methods = PaymentMethod.objects.all()
    context = {
        'payment_methods': payment_methods,
    }
    return render(request, 'expenses/payment_method_list.html', context)


# Budget views

def budget_list(request):
    """List all budgets with current balance calculations"""
    budgets = list(Budget.objects.all())
    
    # Add balance calculation for each budget
    for budget in budgets:
        budget.current_balance = budget.get_current_balance()
    
    context = {
        'budgets': budgets,
    }
    return render(request, 'expenses/budget_list.html', context)


def budget_create(request):
    """Create new budget"""
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save()
            messages.success(request, f'Budget "{budget.name}" created successfully.')
            return redirect('budget_list')
    else:
        form = BudgetForm(initial={
            'start_date': date.today().strftime('%Y-%m-%d')
        })
    
    context = {
        'form': form,
        'title': 'Create New Budget'
    }
    return render(request, 'expenses/budget_form.html', context)


def budget_edit(request, pk):
    """Edit existing budget"""
    budget = get_object_or_404(Budget, pk=pk)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            budget = form.save()
            messages.success(request, f'Budget "{budget.name}" updated successfully.')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget)
    
    context = {
        'form': form,
        'budget': budget,
        'title': f'Edit Budget: {budget.name}'
    }
    return render(request, 'expenses/budget_form.html', context)


def budget_delete(request, pk):
    """Delete budget with confirmation"""
    budget = get_object_or_404(Budget, pk=pk)
    
    # Check if budget has associated months
    month_count = budget.month_set.count()
    
    if request.method == 'POST':
        if month_count > 0:
            messages.error(request, f'Cannot delete budget "{budget.name}" because it has {month_count} associated months.')
        else:
            name = budget.name
            budget.delete()
            messages.success(request, f'Budget "{name}" deleted successfully.')
        return redirect('budget_list')
    
    context = {
        'budget': budget,
        'month_count': month_count,
    }
    return render(request, 'expenses/budget_confirm_delete.html', context)


def expense_item_edit(request, budget_id, pk):
    """Edit expense item due date with month validation"""
    budget = get_object_or_404(Budget, id=budget_id)
    expense_item = get_object_or_404(ExpenseItem, pk=pk, month__budget=budget)
    
    if request.method == 'POST':
        form = ExpenseItemEditForm(request.POST, instance=expense_item)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Due date for "{item.expense.title}" updated successfully.')
            return redirect('expense_detail', budget_id=budget_id, pk=expense_item.expense.pk)
    else:
        form = ExpenseItemEditForm(instance=expense_item)
    
    context = {
        'budget': budget,
        'form': form,
        'expense_item': expense_item,
        'title': f'Edit Expense Item: {expense_item.expense.title}'
    }
    return render(request, 'expenses/expense_item_edit.html', context)
