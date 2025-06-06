from django import forms
from ..models import Payee


class PayeeForm(forms.ModelForm):
    class Meta:
        model = Payee
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Enter payee name", "class": "form-control"}
            )
        }
