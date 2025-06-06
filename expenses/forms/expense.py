from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from ..models import Expense, Month, Payee
from ..fields import SanitizedDecimalField


class ExpenseForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "value": ""}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
        help_text="Format: YYYY-MM-DD",
    )

    day_of_month = forms.IntegerField(
        min_value=1,
        max_value=31,
        required=False,
        widget=forms.NumberInput(attrs={"min": "1", "max": "31"}),
        help_text="Day of month when payment is due (1-31). Auto-filled from start date if not specified.",
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "value": ""}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
        help_text="Format: YYYY-MM-DD",
        required=False,
    )

    notes = forms.CharField(
        max_length=1024,
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "cols": 50,
                "maxlength": 1024,
                "placeholder": "Add additional notes or context about this expense",
                "class": "form-control",
            }
        ),
        help_text="Optional notes or additional context about this expense (max 1024 characters)",
    )

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
        help_text="Per-installment amount for split payments, total amount for others",
    )

    class Meta:
        model = Expense
        fields = [
            "payee",
            "title",
            "expense_type",
            "amount",
            "total_parts",
            "skip_parts",
            "start_date",
            "day_of_month",
            "end_date",
            "notes",
        ]
        widgets = {
            "expense_type": forms.Select(attrs={"id": "expense-type-select"}),
            "total_parts": forms.NumberInput(attrs={"min": "0"}),
            "skip_parts": forms.NumberInput(attrs={"min": "0"}),
            "title": forms.TextInput(attrs={"placeholder": "Enter expense title"}),
        }

    def __init__(self, *args, **kwargs):
        self.budget = kwargs.pop("budget", None)
        super().__init__(*args, **kwargs)
        # Only show non-hidden payees in the dropdown
        payee_field = self.fields["payee"]
        if hasattr(payee_field, "queryset"):
            payee_field.queryset = Payee.objects.filter(hidden_at__isnull=True)  # type: ignore[attr-defined]
        if hasattr(payee_field, "required"):
            payee_field.required = False
        if hasattr(payee_field, "empty_label"):
            payee_field.empty_label = "Select payee (optional)"  # type: ignore[attr-defined]

        # Set default values for new expense creation
        if not self.instance.pk:  # Only for new expenses, not edits
            # Set default expense type to "one_time"
            if not self.fields["expense_type"].initial:
                self.fields["expense_type"].initial = Expense.TYPE_ONE_TIME

            # Set default start date to current date
            if not self.fields["start_date"].initial:
                self.fields["start_date"].initial = date.today()

        # Update amount field attributes for split payments
        self.fields["amount"].widget.attrs.update(
            {
                "data-split-label": "Installment Amount",
                "data-split-help": "Amount for each installment",
                "data-other-label": "Total Amount",
                "data-other-help": "Total amount for this expense",
            }
        )

        # Auto-populate day_of_month from start_date if editing existing expense
        if self.instance and self.instance.pk and hasattr(self.instance, "start_date"):
            if not self.fields["day_of_month"].initial:
                self.fields["day_of_month"].initial = self.instance.start_date.day

        # Handle field restrictions for editing
        if self.instance and self.instance.pk:
            restrictions = self.instance.get_edit_restrictions()

            # If amount cannot be edited, disable the field
            if not restrictions["can_edit_amount"]:
                self.fields["amount"].disabled = True
                self.fields["amount"].help_text = (
                    "Amount cannot be edited because expense has paid items"
                )

            # If date cannot be edited, disable the field
            if not restrictions["can_edit_date"]:
                self.fields["start_date"].disabled = True
                self.fields["start_date"].help_text = (
                    "Date cannot be edited for expenses earlier than next month"
                )

            # Make skip_parts read-only after creation
            self.fields["skip_parts"].disabled = True
            self.fields["skip_parts"].help_text = (
                "Skip parts cannot be changed after expense creation"
            )

            # Store the original values to check for changes later
            self.original_amount = self.instance.amount
            self.original_start_date = self.instance.start_date

    def clean(self):
        """
        Enhanced validation with detailed business rule documentation:

        1. day_of_month validation (1-31 range)
        2. Auto-populate day_of_month from start_date.day if not provided
        3. Type-specific validation:
           - SPLIT_PAYMENT: total_parts > 0, skip_parts < total_parts
           - RECURRING_WITH_END: end_date required and >= start_date
           - Others: total_parts=0, skip_parts=0
        """
        cleaned_data = super().clean()
        if cleaned_data is None:
            return cleaned_data

        expense_type = cleaned_data.get("expense_type")
        total_parts = cleaned_data.get("total_parts", 0)
        skip_parts = cleaned_data.get("skip_parts", 0)
        start_date = cleaned_data.get("start_date")
        day_of_month = cleaned_data.get("day_of_month")
        end_date = cleaned_data.get("end_date")

        # Auto-populate day_of_month from start_date if not provided
        if start_date and not day_of_month:
            cleaned_data["day_of_month"] = start_date.day

        # Additional validation for editing restrictions
        if self.instance and self.instance.pk:
            # Double-check edit permissions (in case someone bypasses frontend)
            if not self.instance.can_be_edited():
                raise ValidationError("This expense cannot be edited.")

            # Check amount editing permissions
            if hasattr(self, "original_amount") and not self.instance.can_edit_amount():
                amount = cleaned_data.get("amount")
                if amount != self.original_amount:
                    raise ValidationError("Amount cannot be changed for this expense.")

            # Check date editing permissions
            if (
                hasattr(self, "original_start_date")
                and not self.instance.can_edit_date()
            ):
                start_date = cleaned_data.get("start_date")
                if start_date != self.original_start_date:
                    raise ValidationError(
                        "Date cannot be changed for expenses earlier than next month."
                    )

            # When date editing is allowed, validate new date restrictions
            if hasattr(self, "original_start_date") and self.instance.can_edit_date():
                start_date = cleaned_data.get("start_date")
                if start_date and start_date != self.original_start_date:
                    # For one-time expenses, allow moving back to the most recent month
                    if self.instance.expense_type == self.instance.TYPE_ONE_TIME:
                        most_recent_month = Month.get_most_recent(
                            budget=self.instance.budget
                        )
                        if most_recent_month:
                            # Allow dates from most recent month onward
                            earliest_allowed = date(
                                most_recent_month.year, most_recent_month.month, 1
                            )
                            if start_date < earliest_allowed:
                                most_recent_name = earliest_allowed.strftime("%B %Y")
                                raise ValidationError(
                                    f"One-time expense dates cannot be earlier than the most recent month ({most_recent_name})."
                                )
                    else:
                        # For other expense types, use the original "next month" restriction
                        next_month_date = self.instance.get_next_month_date()
                        if next_month_date and start_date < next_month_date:
                            raise ValidationError(
                                f'New date must be no earlier than the next month ({next_month_date.strftime("%Y-%m-%d")}).'
                            )

        # Type-specific validation
        if expense_type == Expense.TYPE_SPLIT_PAYMENT and total_parts <= 0:
            raise ValidationError("Split payments must have total_parts > 0")

        if (
            expense_type
            in [
                Expense.TYPE_ENDLESS_RECURRING,
                Expense.TYPE_ONE_TIME,
                Expense.TYPE_RECURRING_WITH_END,
            ]
            and total_parts > 0
        ):
            raise ValidationError("Only split payments can have total_parts > 0")

        # Validate skip_parts
        if expense_type == Expense.TYPE_SPLIT_PAYMENT:
            if skip_parts < 0:
                raise ValidationError("Skip parts cannot be negative")
            if skip_parts >= total_parts:
                raise ValidationError("Skip parts must be less than total parts count")
        elif skip_parts > 0:
            raise ValidationError(
                "Skip parts can only be used with split payment expenses"
            )

        if expense_type == Expense.TYPE_RECURRING_WITH_END:
            if not end_date:
                raise ValidationError(
                    "Recurring with end date expenses must have an end date"
                )
            if end_date and start_date and end_date < start_date:
                raise ValidationError("End date must be on or after the start date")

        if expense_type != Expense.TYPE_RECURRING_WITH_END and end_date:
            raise ValidationError(
                "Only recurring with end date expenses can have an end date"
            )

        # Validate start date is not earlier than currently active month for this budget
        if start_date and self.budget:
            most_recent_month = Month.get_most_recent(budget=self.budget)
            if most_recent_month:
                # Get first day of the most recent month for this budget
                current_month_start = date(
                    most_recent_month.year, most_recent_month.month, 1
                )
                if start_date < current_month_start:
                    raise ValidationError(
                        f"Start date cannot be earlier than the currently active month ({most_recent_month})"
                    )

        return cleaned_data
