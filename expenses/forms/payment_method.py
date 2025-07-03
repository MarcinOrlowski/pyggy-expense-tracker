from django import forms
from ..models import PaymentMethod


class PaymentMethodForm(forms.ModelForm):
    """Form for creating and editing payment methods"""

    class Meta:
        """Form configuration for PaymentMethod model."""

        model = PaymentMethod
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter payment method name",
                }
            ),
        }
