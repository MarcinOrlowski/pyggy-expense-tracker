from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models import PaymentMethod
from ..forms import PaymentMethodForm


def payment_method_list(request):
    """List all payment methods"""
    payment_methods = PaymentMethod.objects.all()
    context = {
        "payment_methods": payment_methods,
    }
    return render(request, "expenses/payment_method_list.html", context)


def payment_method_create(request):
    """Create a new payment method"""
    if request.method == "POST":
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment method created successfully.")
            return redirect("payment_method_list")
    else:
        form = PaymentMethodForm()

    context = {
        "form": form,
        "title": "Create Payment Method",
    }
    return render(request, "expenses/payment_method_form.html", context)


def payment_method_edit(request, pk):
    """Edit an existing payment method"""
    payment_method = get_object_or_404(PaymentMethod, pk=pk)

    if request.method == "POST":
        form = PaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment method updated successfully.")
            return redirect("payment_method_list")
    else:
        form = PaymentMethodForm(instance=payment_method)

    context = {
        "form": form,
        "payment_method": payment_method,
        "title": "Edit Payment Method",
    }
    return render(request, "expenses/payment_method_form.html", context)


def payment_method_delete(request, pk):
    """Delete a payment method"""
    payment_method = get_object_or_404(PaymentMethod, pk=pk)

    if request.method == "POST":
        if not payment_method.can_be_deleted():
            payment_count = payment_method.payment_set.count()
            messages.error(
                request,
                f'Cannot delete payment method "{payment_method.name}" because it is used by {payment_count} payment(s).',
            )
        else:
            payment_method.delete()
            messages.success(request, "Payment method deleted successfully.")
        return redirect("payment_method_list")

    context = {
        "payment_method": payment_method,
        "can_delete": payment_method.can_be_deleted(),
        "payment_count": (
            payment_method.payment_set.count()
            if not payment_method.can_be_deleted()
            else 0
        ),
    }
    return render(request, "expenses/payment_method_confirm_delete.html", context)
