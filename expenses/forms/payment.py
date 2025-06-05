from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from ..models import ExpenseItem, PaymentMethod
from ..fields import SanitizedDecimalField


class PaymentForm(forms.ModelForm):
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
        required=False,
    )
    payment_id = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Optional payment reference ID or transaction number"}
        ),
        help_text="Optional payment reference ID, transaction number, or confirmation code",
    )

    class Meta:
        model = ExpenseItem
        fields = ["payment_date", "status", "payment_method", "payment_id"]
        widgets = {
            "status": forms.Select(),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            return cleaned_data

        status = cleaned_data.get("status")
        payment_date = cleaned_data.get("payment_date")

        if status == "paid" and not payment_date:
            raise ValidationError("Payment date is required when marking as paid")

        if status == "pending" and payment_date:
            cleaned_data["payment_date"] = None

        return cleaned_data


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
