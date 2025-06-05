from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from ..models import Budget
from ..fields import SanitizedDecimalField


class BudgetForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        help_text='Format: YYYY-MM-DD'
    )
    
    initial_amount = SanitizedDecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={
            'placeholder': '100, -200.03, €50',
            'class': 'form-control',
            'value': '0'
        }),
        help_text="Supports international formats including negative values: 100, -200.03, €50"
    )
    
    class Meta:
        model = Budget
        fields = ['name', 'start_date', 'initial_amount']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter budget name',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.instance_pk = kwargs.get('instance').pk if kwargs.get('instance') else None
        super().__init__(*args, **kwargs)
        
        # Disable start_date field if budget has existing months
        if self.instance and self.instance.pk and self.instance.month_set.exists():
            self.fields['start_date'].disabled = True
            self.fields['start_date'].help_text = 'Cannot change start date when months exist'
    
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < date.today():
            # Allow past dates only if this budget has no months
            if self.instance_pk:
                if self.instance.month_set.exists():
                    raise ValidationError('Start date cannot be in the past when budget has existing months')
        return start_date