from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from decimal import Decimal
from ..models import ExpenseItem, PaymentMethod, Payment
from ..fields import SanitizedDecimalField


class PaymentForm(forms.ModelForm):
    amount = SanitizedDecimalField(
        max_digits=13,
        decimal_places=2,
        min_value=0.01,
        widget=forms.TextInput(
            attrs={
                "placeholder": "25.50",
                "class": "form-control",
            }
        ),
        help_text="Payment amount (cannot exceed remaining balance)",
    )
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.all(),
        required=False,
        empty_label="Select payment method (optional)",
    )
    payment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"],
        required=True,
    )
    transaction_id = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Optional transaction reference (e.g., bank transfer ID, check number)"
            }
        ),
        help_text="Optional transaction reference (e.g., bank transfer ID, check number, receipt number)",
    )

    class Meta:
        """Form configuration for Payment model."""

        model = Payment
        fields = ["amount", "payment_date", "payment_method", "transaction_id"]

    def __init__(self, *args, **kwargs):
        self.expense_item = kwargs.pop("expense_item", None)
        super().__init__(*args, **kwargs)

        if self.expense_item:
            # Set remaining amount as placeholder and default
            remaining = self.expense_item.get_remaining_amount()
            # remaining is negative when money is still owed
            amount_still_owed = abs(remaining) if remaining < 0 else Decimal("0.00")
            amount_widget = self.fields["amount"].widget
            amount_widget.attrs["placeholder"] = f"Max: {amount_still_owed}"
            self.fields["amount"].help_text = (
                f"Payment amount (max: {amount_still_owed})"
            )
            if not self.initial.get("amount") and amount_still_owed > 0:
                self.initial["amount"] = amount_still_owed

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount and self.expense_item:
            remaining = self.expense_item.get_remaining_amount()
            # remaining is negative when money is still owed
            # Convert to positive amount still owed for validation
            amount_still_owed = abs(remaining) if remaining < 0 else Decimal("0.00")
            if amount > amount_still_owed:
                raise ValidationError(
                    f"Payment amount cannot exceed remaining balance of {amount_still_owed}"
                )
        return amount

    def save(self, commit=True):
        payment = super().save(commit=False)
        if self.expense_item:
            payment.expense_item = self.expense_item
        if commit:
            payment.save()
        return payment


class ExpenseItemEditForm(forms.ModelForm):
    amount = SanitizedDecimalField(
        max_digits=13,
        decimal_places=2,
        min_value=0.01,
        widget=forms.TextInput(
            attrs={
                "placeholder": "10.50, 10,50, $10.50, €10,50",
                "class": "form-control",
            }
        ),
        help_text="Amount for this specific payment instance",
    )

    due_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
        help_text="Due date must be within the same month",
    )

    class Meta:
        """Form configuration for ExpenseItem model."""

        model = ExpenseItem
        fields = ["amount", "due_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set helpful information about month restriction for due date
        if self.instance and self.instance.pk:
            start_date, end_date = self.instance.get_allowed_month_range()
            month_name = date(
                self.instance.month.year, self.instance.month.month, 1
            ).strftime("%B %Y")
            self.fields["due_date"].help_text = (
                f"Date must be within {month_name} ({start_date} to {end_date})"
            )

    def clean_due_date(self):
        due_date = self.cleaned_data.get("due_date")

        if due_date and self.instance and self.instance.pk:
            # Use the same validation logic as ExpenseItem.get_allowed_month_range()
            start_date, end_date = self.instance.get_allowed_month_range()

            if not (start_date <= due_date <= end_date):
                month_name = date(
                    self.instance.month.year, self.instance.month.month, 1
                ).strftime("%B %Y")
                raise ValidationError(f"Due date must be within {month_name}")

        return due_date
