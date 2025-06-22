from django import forms
from django.core.exceptions import ValidationError
from ..models import Budget
from ..fields import SanitizedDecimalField


class BudgetForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
        help_text="Format: YYYY-MM-DD",
    )

    initial_amount = SanitizedDecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(
            attrs={
                "placeholder": "100, -200.03, €50",
                "class": "form-control",
                "value": "0",
            }
        ),
        help_text="Supports international formats including negative values: 100, -200.03, €50",
    )

    class Meta:
        model = Budget
        fields = ["name", "start_date", "initial_amount", "currency"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Enter budget name", "class": "form-control"}
            ),
            "currency": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable start_date field if budget has existing months
        if (
            self.instance
            and self.instance.pk
            and self.instance.budgetmonth_set.exists()
        ):
            self.fields["start_date"].disabled = True
            self.fields["start_date"].help_text = (
                "Cannot change start date when months exist"
            )

    def clean_start_date(self):
        start_date = self.cleaned_data.get("start_date")
        # For existing budgets with months, start_date cannot be changed at all
        if self.instance and self.instance.pk:
            if (
                start_date != self.instance.start_date
                and self.instance.budgetmonth_set.exists()
            ):
                raise ValidationError(
                    "Start date cannot be changed when budget has existing months"
                )
        return start_date
