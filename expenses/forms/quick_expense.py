from django import forms
from typing import cast
from ..models import Payee
from ..fields import SanitizedDecimalField


class QuickExpenseForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Coffee, groceries, gas...",
                "class": "form-control",
            }
        ),
        help_text="Brief description of the expense",
    )

    payee = forms.ModelChoiceField(
        queryset=Payee.objects.filter(hidden_at__isnull=True),
        required=False,
        empty_label="Select payee (optional)",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    amount = SanitizedDecimalField(
        max_digits=13,
        decimal_places=2,
        min_value=0.01,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Amount (e.g., 10.50)",
                "class": "form-control",
            }
        ),
        help_text="Expense amount",
    )

    mark_as_paid = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        help_text="Automatically mark this expense as paid with current date",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show non-hidden payees in the dropdown
        payee_field = cast(forms.ModelChoiceField, self.fields["payee"])
        payee_field.queryset = Payee.objects.filter(hidden_at__isnull=True).order_by(
            "name"
        )
