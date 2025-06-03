from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Expense, ExpenseItem, PaymentMethod, Payee, Month, Budget
from .fields import SanitizedDecimalField


class ExpenseForm(forms.ModelForm):
    started_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'value': ''}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        help_text='Format: YYYY-MM-DD'
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'value': ''}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        help_text='Format: YYYY-MM-DD',
        required=False
    )
    
    notes = forms.CharField(
        max_length=1024,
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'cols': 50,
            'maxlength': 1024,
            'placeholder': 'Add additional notes or context about this expense',
            'class': 'form-control'
        }),
        help_text="Optional notes or additional context about this expense (max 1024 characters)"
    )
    
    total_amount = SanitizedDecimalField(
        max_digits=13,
        decimal_places=2,
        min_value=0.01,
        widget=forms.TextInput(attrs={
            'placeholder': '10.50, 10,50, $10.50, €10,50',
            'class': 'form-control'
        }),
        help_text="Supports international formats: 10.50, 10,50, $10.50, €10,50"
    )
    
    class Meta:
        model = Expense
        fields = ['payee', 'title', 'expense_type', 'total_amount', 'installments_count', 'initial_installment', 'started_at', 'end_date', 'notes']
        widgets = {
            'expense_type': forms.Select(attrs={'id': 'expense-type-select'}),
            'installments_count': forms.NumberInput(attrs={'min': '0'}),
            'initial_installment': forms.NumberInput(attrs={'min': '0'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter expense title'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.budget = kwargs.pop('budget', None)
        super().__init__(*args, **kwargs)
        # Only show non-hidden payees in the dropdown
        self.fields['payee'].queryset = Payee.objects.filter(hidden_at__isnull=True)
        self.fields['payee'].required = False
        self.fields['payee'].empty_label = "Select payee (optional)"
        
        # Update total_amount field attributes for split payments
        self.fields['total_amount'].widget.attrs.update({
            'data-split-label': 'Monthly Installment Amount',
            'data-split-help': 'Amount for each monthly installment',
            'data-other-label': 'Total Amount', 
            'data-other-help': 'Total amount for this expense'
        })
        
        # Handle field restrictions for editing
        if self.instance and self.instance.pk:
            restrictions = self.instance.get_edit_restrictions()
            
            # If amount cannot be edited, disable the field
            if not restrictions['can_edit_amount']:
                self.fields['total_amount'].disabled = True
                self.fields['total_amount'].help_text = 'Amount cannot be edited because expense has paid items'
            
            # Make initial_installment read-only after creation
            self.fields['initial_installment'].disabled = True
            self.fields['initial_installment'].help_text = 'Initial installment cannot be changed after expense creation'
            
            # Store the original amount to check for changes later
            self.original_amount = self.instance.total_amount
    
    def clean(self):
        cleaned_data = super().clean()
        expense_type = cleaned_data.get('expense_type')
        installments_count = cleaned_data.get('installments_count', 0)
        initial_installment = cleaned_data.get('initial_installment', 0)
        started_at = cleaned_data.get('started_at')
        end_date = cleaned_data.get('end_date')
        
        # Additional validation for editing restrictions
        if self.instance and self.instance.pk:
            # Double-check edit permissions (in case someone bypasses frontend)
            if not self.instance.can_be_edited():
                raise ValidationError('This expense cannot be edited.')
            
            # Check amount editing permissions
            if hasattr(self, 'original_amount') and not self.instance.can_edit_amount():
                total_amount = cleaned_data.get('total_amount')
                if total_amount != self.original_amount:
                    raise ValidationError('Amount cannot be changed for this expense.')
        
        if expense_type == Expense.TYPE_SPLIT_PAYMENT and installments_count <= 0:
            raise ValidationError('Split payments must have installments count greater than 0')
        
        if expense_type in [Expense.TYPE_ENDLESS_RECURRING, Expense.TYPE_ONE_TIME, Expense.TYPE_RECURRING_WITH_END] and installments_count > 0:
            raise ValidationError('Only split payments can have installments count greater than 0')
        
        # Validate initial_installment
        if expense_type == Expense.TYPE_SPLIT_PAYMENT:
            if initial_installment < 0:
                raise ValidationError('Initial installment cannot be negative')
            if initial_installment >= installments_count:
                raise ValidationError('Initial installment must be less than total installments count')
        elif initial_installment > 0:
            raise ValidationError('Initial installment can only be used with split payment expenses')
        
        if expense_type == Expense.TYPE_RECURRING_WITH_END:
            if not end_date:
                raise ValidationError('Recurring with end date expenses must have an end date')
            if end_date and started_at and end_date < started_at:
                raise ValidationError('End date must be on or after the start date')
        
        if expense_type != Expense.TYPE_RECURRING_WITH_END and end_date:
            raise ValidationError('Only recurring with end date expenses can have an end date')
        
        # Validate start date is not earlier than currently active month for this budget
        if started_at and self.budget:
            most_recent_month = Month.get_most_recent(budget=self.budget)
            if most_recent_month:
                # Get first day of the most recent month for this budget
                current_month_start = date(most_recent_month.year, most_recent_month.month, 1)
                if started_at < current_month_start:
                    raise ValidationError(f'Start date cannot be earlier than the currently active month ({most_recent_month})')
        
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


class BudgetForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        help_text='Format: YYYY-MM-DD'
    )
    
    initial_amount = SanitizedDecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.TextInput(attrs={
            'placeholder': '100.00, 100,00, $100.00, €100,00',
            'class': 'form-control'
        }),
        help_text="Supports international formats: 100.00, 100,00, $100.00, €100,00"
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