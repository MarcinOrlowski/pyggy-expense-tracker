from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date
from .models import Expense, ExpenseItem, Month, Payee, PaymentMethod
from .forms import ExpenseForm, PaymentForm, PayeeForm


def dashboard(request):
    """Display current month summary with pending and paid payments"""
    current_date = date.today()
    
    # Check if any months exist in the system
    has_any_months = Month.objects.exists()
    
    try:
        current_month = Month.objects.get(year=current_date.year, month=current_date.month)
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
    except Month.DoesNotExist:
        all_expense_items = []
        pending_items = []
        paid_items = []
        total_pending = 0
        total_paid = 0
        total_month = 0
        current_month = None
    
    # Create normalized summary data for the include
    dashboard_summary = {
        'total': total_month,
        'paid': total_paid,
        'pending': total_pending,
        'paid_count': len(paid_items),
        'pending_count': len(pending_items),
    }
    
    context = {
        # Original context for backward compatibility
        'current_month': current_month,
        'pending_items': pending_items,
        'paid_items': paid_items,
        'total_pending': total_pending,
        'total_paid': total_paid,
        'total_month': total_month,
        'current_date': current_date,
        'has_any_months': has_any_months,
        # New normalized context for includes
        'all_expense_items': all_expense_items,
        'dashboard_summary': dashboard_summary,
        'not_has_any_months': not has_any_months,
        'not_current_month': current_month is None,
    }
    return render(request, 'expenses/dashboard.html', context)


def expense_list(request):
    """List active expenses with filtering options"""
    expenses = Expense.objects.filter(closed_at__isnull=True).select_related('payee')
    
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
        'expenses': expenses,
        'payees': payees,
        'expense_types': Expense.EXPENSE_TYPES,
        'selected_type': expense_type,
        'selected_payee': int(payee_id) if payee_id else None,
    }
    return render(request, 'expenses/expense_list.html', context)


def expense_create(request):
    """Create new expense with form validation"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save()
            # Handle expense items creation if it starts in current month
            from .services import handle_new_expense
            handle_new_expense(expense)
            messages.success(request, f'Expense "{expense.title}" created successfully.')
            return redirect('expense_detail', pk=expense.pk)
    else:
        # Set default start date to current month's first day
        most_recent_month = Month.get_most_recent()
        if most_recent_month:
            default_date = date(most_recent_month.year, most_recent_month.month, 1)
        else:
            default_date = date.today()
        
        form = ExpenseForm(initial={
            'started_at': default_date.strftime('%Y-%m-%d')
        })
    
    context = {
        'form': form,
        'title': 'Create New Expense'
    }
    return render(request, 'expenses/expense_form.html', context)


def expense_detail(request, pk):
    """Display expense details and related items"""
    expense = get_object_or_404(Expense, pk=pk)
    expense_items = ExpenseItem.objects.filter(
        expense=expense
    ).select_related('month', 'payment_method').order_by('due_date')
    
    context = {
        'expense': expense,
        'expense_items': expense_items,
    }
    return render(request, 'expenses/expense_detail.html', context)


def expense_edit(request, pk):
    """Edit existing expense"""
    expense = get_object_or_404(Expense, pk=pk)
    
    if request.method == 'POST':
        original_start_date = expense.started_at
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            expense = form.save()
            # If start date changed and now starts in current month, handle expense items
            if original_start_date != expense.started_at:
                from .services import handle_new_expense
                handle_new_expense(expense)
            messages.success(request, f'Expense "{expense.title}" updated successfully.')
            return redirect('expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense)
    
    context = {
        'form': form,
        'expense': expense,
        'title': f'Edit Expense: {expense.title}'
    }
    return render(request, 'expenses/expense_form.html', context)


def expense_delete(request, pk):
    """Delete expense with confirmation"""
    expense = get_object_or_404(Expense, pk=pk)
    
    if request.method == 'POST':
        title = expense.title
        expense.delete()
        messages.success(request, f'Expense "{title}" deleted successfully.')
        return redirect('expense_list')
    
    context = {
        'expense': expense,
    }
    return render(request, 'expenses/expense_confirm_delete.html', context)


def month_list(request):
    """List all months"""
    months = Month.objects.all()
    
    # Get next allowed month for button text
    next_allowed = Month.get_next_allowed_month()
    
    context = {
        'months': months,
        'next_allowed_month': next_allowed,
    }
    return render(request, 'expenses/month_list.html', context)


def month_detail(request, year, month):
    """Display month details with expense items"""
    month_obj = get_object_or_404(Month, year=year, month=month)
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


def month_delete(request, year, month):
    """Delete month with validation"""
    month_obj = get_object_or_404(Month, year=year, month=month)
    
    # Check if this is the most recent month
    most_recent = Month.get_most_recent()
    if most_recent != month_obj:
        messages.error(request, 'You can only delete the most recent month.')
        return redirect('month_list')
    
    # Check if month has paid expenses
    if month_obj.has_paid_expenses():
        messages.error(request, f'Cannot delete month {month_obj} because it contains paid expenses.')
        return redirect('month_list')
    
    if request.method == 'POST':
        month_str = str(month_obj)
        month_obj.delete()
        messages.success(request, f'Month {month_str} deleted successfully.')
        return redirect('month_list')
    
    # Count expense items that will be deleted
    expense_items_count = month_obj.expenseitem_set.count()
    
    context = {
        'month': month_obj,
        'expense_items_count': expense_items_count,
    }
    return render(request, 'expenses/month_confirm_delete.html', context)


def month_process(request):
    """Process new month generation"""
    if request.method == 'POST':
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
        
        # Check if this is the next allowed month
        next_allowed = Month.get_next_allowed_month()
        if not next_allowed:
            # No months exist, this is initial seeding - allow any valid month
            if not (2020 <= year <= 2099) or not (1 <= month <= 12):
                messages.error(request, 'Please enter a valid year (2020-2099) and month (1-12).')
                return redirect('month_process')
        else:
            # Months exist, enforce sequential creation
            if year != next_allowed['year'] or month != next_allowed['month']:
                messages.error(request, f"You can only create month {next_allowed['year']}-{next_allowed['month']:02d} (the next sequential month).")
                return redirect('month_process')
        
        try:
            from .services import process_new_month
            month_obj = process_new_month(year, month)
            messages.success(request, f'Month {month_obj} processed successfully.')
            return redirect('month_detail', year=year, month=month)
        except Exception as e:
            messages.error(request, f'Error processing month: {str(e)}')
    
    # Show form for selecting month to process
    next_allowed = Month.get_next_allowed_month()
    if not next_allowed:
        # No months exist, allow user to choose initial month
        from datetime import date
        today = date.today()
        context = {
            'suggested_year': today.year,
            'suggested_month': today.month,
            'no_months_exist': True,
        }
    else:
        context = {
            'suggested_year': next_allowed['year'],
            'suggested_month': next_allowed['month'],
            'most_recent_month': Month.get_most_recent(),
        }
    return render(request, 'expenses/month_process.html', context)


def expense_item_pay(request, pk):
    """Record payment for expense item"""
    expense_item = get_object_or_404(ExpenseItem, pk=pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=expense_item)
        if form.is_valid():
            item = form.save()
            if item.status == 'paid':
                # Check if expense should be completed
                from .services import check_expense_completion
                check_expense_completion(item.expense)
            messages.success(request, 'Payment recorded successfully.')
            return redirect('expense_detail', pk=expense_item.expense.pk)
    else:
        form = PaymentForm(instance=expense_item, initial={
            'payment_date': datetime.now().strftime('%Y-%m-%dT%H:%M'),
            'status': 'paid'
        })
    
    context = {
        'form': form,
        'expense_item': expense_item,
        'title': f'Record Payment: {expense_item.expense.title}'
    }
    return render(request, 'expenses/payment_form.html', context)


def expense_item_unpay(request, pk):
    """Mark expense item as unpaid"""
    expense_item = get_object_or_404(ExpenseItem, pk=pk)
    
    if request.method == 'POST':
        expense_item.status = 'pending'
        expense_item.payment_date = None
        expense_item.payment_method = None
        expense_item.save()
        messages.success(request, 'Payment unmarked successfully.')
        return redirect('expense_detail', pk=expense_item.expense.pk)
    
    context = {
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
