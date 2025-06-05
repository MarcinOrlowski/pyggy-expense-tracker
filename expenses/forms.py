from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Expense, ExpenseItem, PaymentMethod, Payee, Month, Budget
from .fields import SanitizedDecimalField


class ExpenseForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'value': ''}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        help_text='Format: YYYY-MM-DD'
    )
    
    day_of_month = forms.IntegerField(
        min_value=1,
        max_value=31,
        required=False,
        widget=forms.NumberInput(attrs={'min': '1', 'max': '31'}),
        help_text='Day of month when payment is due (1-31). Auto-filled from start date if not specified.'
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
    
    amount = SanitizedDecimalField(
        max_digits=13,
        decimal_places=2,
        min_value=0.01,
        widget=forms.TextInput(attrs={
            'placeholder': '10.50, 10,50, $10.50, €10,50',
            'class': 'form-control'
        }),
        help_text="Per-installment amount for split payments, total amount for others"
    )
    
    class Meta:
        model = Expense
        fields = ['payee', 'title', 'expense_type', 'amount', 'total_parts', 'skip_parts', 'start_date', 'day_of_month', 'end_date', 'notes']
        widgets = {
            'expense_type': forms.Select(attrs={'id': 'expense-type-select'}),
            'total_parts': forms.NumberInput(attrs={'min': '0'}),
            'skip_parts': forms.NumberInput(attrs={'min': '0'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter expense title'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.budget = kwargs.pop('budget', None)
        super().__init__(*args, **kwargs)
        # Only show non-hidden payees in the dropdown
        self.fields['payee'].queryset = Payee.objects.filter(hidden_at__isnull=True)
        self.fields['payee'].required = False
        self.fields['payee'].empty_label = "Select payee (optional)"
        
        # Update amount field attributes for split payments
        self.fields['amount'].widget.attrs.update({
            'data-split-label': 'Installment Amount',
            'data-split-help': 'Amount for each installment',
            'data-other-label': 'Total Amount', 
            'data-other-help': 'Total amount for this expense'
        })
        
        # Auto-populate day_of_month from start_date if editing existing expense
        if self.instance and self.instance.pk and hasattr(self.instance, 'start_date'):
            if not self.fields['day_of_month'].initial:
                self.fields['day_of_month'].initial = self.instance.start_date.day
        
        # Handle field restrictions for editing
        if self.instance and self.instance.pk:
            restrictions = self.instance.get_edit_restrictions()
            
            # If amount cannot be edited, disable the field
            if not restrictions['can_edit_amount']:
                self.fields['amount'].disabled = True
                self.fields['amount'].help_text = 'Amount cannot be edited because expense has paid items'
            
            # If date cannot be edited, disable the field
            if not restrictions['can_edit_date']:
                self.fields['start_date'].disabled = True
                self.fields['start_date'].help_text = 'Date cannot be edited for expenses earlier than next month'
            
            # Make skip_parts read-only after creation
            self.fields['skip_parts'].disabled = True
            self.fields['skip_parts'].help_text = 'Skip parts cannot be changed after expense creation'
            
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
        expense_type = cleaned_data.get('expense_type')
        total_parts = cleaned_data.get('total_parts', 0)
        skip_parts = cleaned_data.get('skip_parts', 0)
        start_date = cleaned_data.get('start_date')
        day_of_month = cleaned_data.get('day_of_month')
        end_date = cleaned_data.get('end_date')
        
        # Auto-populate day_of_month from start_date if not provided
        if start_date and not day_of_month:
            cleaned_data['day_of_month'] = start_date.day
        
        # Additional validation for editing restrictions
        if self.instance and self.instance.pk:
            # Double-check edit permissions (in case someone bypasses frontend)
            if not self.instance.can_be_edited():
                raise ValidationError('This expense cannot be edited.')
            
            # Check amount editing permissions
            if hasattr(self, 'original_amount') and not self.instance.can_edit_amount():
                amount = cleaned_data.get('amount')
                if amount != self.original_amount:
                    raise ValidationError('Amount cannot be changed for this expense.')
            
            # Check date editing permissions
            if hasattr(self, 'original_start_date') and not self.instance.can_edit_date():
                start_date = cleaned_data.get('start_date')
                if start_date != self.original_start_date:
                    raise ValidationError('Date cannot be changed for expenses earlier than next month.')
            
            # When date editing is allowed, validate new date restrictions
            if hasattr(self, 'original_start_date') and self.instance.can_edit_date():
                start_date = cleaned_data.get('start_date')
                if start_date and start_date != self.original_start_date:
                    # For one-time expenses, allow moving back to the most recent month
                    if self.instance.expense_type == self.instance.TYPE_ONE_TIME:
                        most_recent_month = Month.get_most_recent(budget=self.instance.budget)
                        if most_recent_month:
                            # Allow dates from most recent month onward
                            earliest_allowed = date(most_recent_month.year, most_recent_month.month, 1)
                            if start_date < earliest_allowed:
                                most_recent_name = earliest_allowed.strftime("%B %Y")
                                raise ValidationError(f'One-time expense dates cannot be earlier than the most recent month ({most_recent_name}).')
                    else:
                        # For other expense types, use the original "next month" restriction
                        next_month_date = self.instance.get_next_month_date()
                        if next_month_date and start_date < next_month_date:
                            raise ValidationError(f'New date must be no earlier than the next month ({next_month_date.strftime("%Y-%m-%d")}).')
        
        # Type-specific validation
        if expense_type == Expense.TYPE_SPLIT_PAYMENT and total_parts <= 0:
            raise ValidationError('Split payments must have total_parts > 0')
        
        if expense_type in [Expense.TYPE_ENDLESS_RECURRING, Expense.TYPE_ONE_TIME, Expense.TYPE_RECURRING_WITH_END] and total_parts > 0:
            raise ValidationError('Only split payments can have total_parts > 0')
        
        # Validate skip_parts
        if expense_type == Expense.TYPE_SPLIT_PAYMENT:
            if skip_parts < 0:
                raise ValidationError('Skip parts cannot be negative')
            if skip_parts >= total_parts:
                raise ValidationError('Skip parts must be less than total parts count')
        elif skip_parts > 0:
            raise ValidationError('Skip parts can only be used with split payment expenses')
        
        if expense_type == Expense.TYPE_RECURRING_WITH_END:
            if not end_date:
                raise ValidationError('Recurring with end date expenses must have an end date')
            if end_date and start_date and end_date < start_date:
                raise ValidationError('End date must be on or after the start date')
        
        if expense_type != Expense.TYPE_RECURRING_WITH_END and end_date:
            raise ValidationError('Only recurring with end date expenses can have an end date')
        
        # Validate start date is not earlier than currently active month for this budget
        if start_date and self.budget:
            most_recent_month = Month.get_most_recent(budget=self.budget)
            if most_recent_month:
                # Get first day of the most recent month for this budget
                current_month_start = date(most_recent_month.year, most_recent_month.month, 1)
                if start_date < current_month_start:
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


class ExpenseItemEditForm(forms.ModelForm):
    amount = SanitizedDecimalField(
        max_digits=13,
        decimal_places=2,
        min_value=0.01,
        widget=forms.TextInput(attrs={
            'placeholder': '10.50, 10,50, $10.50, €10,50',
            'class': 'form-control'
        }),
        help_text='Amount for this specific payment instance'
    )
    
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        help_text='Due date must be within the same month'
    )
    
    class Meta:
        model = ExpenseItem
        fields = ['amount', 'due_date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set helpful information about month restriction for due date
        if self.instance and self.instance.pk:
            month_name = date(self.instance.month.year, self.instance.month.month, 1).strftime("%B %Y")
            self.fields['due_date'].help_text = f'Date must be within {month_name}'
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        
        if due_date and self.instance and self.instance.pk:
            # Restrict due date to the same month as the expense item
            month_year = (self.instance.month.year, self.instance.month.month)
            due_year_month = (due_date.year, due_date.month)
            
            if month_year != due_year_month:
                month_name = date(self.instance.month.year, self.instance.month.month, 1).strftime("%B %Y")
                raise ValidationError(f'Due date must be within {month_name}')
        
        return due_date


class PaymentMethodForm(forms.ModelForm):
    """Form for creating and editing payment methods"""
    
    class Meta:
        model = PaymentMethod
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter payment method name'}),
        }