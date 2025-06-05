from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from ..models import Payee, Expense
from ..forms import PayeeForm


def payee_list(request):
    """List all payees"""
    show_hidden = request.GET.get('show_hidden', 'false') == 'true'
    
    if show_hidden:
        payees = Payee.objects.all()
    else:
        payees = Payee.objects.filter(hidden_at__isnull=True)
    
    # Add expense count for each payee
    for payee in payees:
        payee.expense_count = Expense.objects.filter(payee=payee).count()  # type: ignore[attr-defined]
    
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