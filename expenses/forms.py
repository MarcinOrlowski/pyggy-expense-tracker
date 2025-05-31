from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Expense, ExpenseItem, PaymentMethod, Payee, Month


class ExpenseForm(forms.ModelForm):
    started_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'value': ''}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        help_text='Format: YYYY-MM-DD'
    )
    
    class Meta:
        model = Expense
        fields = ['payee', 'title', 'expense_type', 'total_amount', 'installments_count', 'started_at']
        widgets = {
            'expense_type': forms.Select(attrs={'id': 'expense-type-select'}),
            'installments_count': forms.NumberInput(attrs={'min': '0'}),
            'total_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter expense title'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show non-hidden payees in the dropdown
        self.fields['payee'].queryset = Payee.objects.filter(hidden_at__isnull=True)
        self.fields['payee'].required = False
        self.fields['payee'].empty_label = "Select payee (optional)"
    
    def clean(self):
        cleaned_data = super().clean()
        expense_type = cleaned_data.get('expense_type')
        installments_count = cleaned_data.get('installments_count', 0)
        started_at = cleaned_data.get('started_at')
        
        if expense_type == 'split_payment' and installments_count <= 0:
            raise ValidationError('Split payments must have installments count greater than 0')
        
        if expense_type in ['endless_recurring', 'one_time'] and installments_count > 0:
            raise ValidationError('Only split payments can have installments count greater than 0')
        
        # Validate start date is not earlier than current month
        if started_at:
            most_recent_month = Month.get_most_recent()
            if most_recent_month:
                # Get first day of the most recent month
                current_month_start = date(most_recent_month.year, most_recent_month.month, 1)
                if started_at < current_month_start:
                    raise ValidationError(f'Start date cannot be earlier than the current month ({most_recent_month})')
        
        return cleaned_data


class PaymentForm(forms.ModelForm):
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.all(),
        required=False,
        empty_label="Select payment method (optional)"
    )
    payment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S'],
        required=False
    )
    payment_id = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Optional payment reference ID or transaction number'
        }),
        help_text='Optional payment reference ID, transaction number, or confirmation code'
    )
    
    class Meta:
        model = ExpenseItem
        fields = ['payment_date', 'status', 'payment_method', 'payment_id']
        widgets = {
            'status': forms.Select(),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        payment_date = cleaned_data.get('payment_date')
        
        if status == 'paid' and not payment_date:
            raise ValidationError('Payment date is required when marking as paid')
        
        if status == 'pending' and payment_date:
            cleaned_data['payment_date'] = None
        
        return cleaned_data


class PayeeForm(forms.ModelForm):
    class Meta:
        model = Payee
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter payee name',
                'class': 'form-control'
            })
        }