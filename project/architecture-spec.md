# Architecture Specification

Expense Tracker PoC Implementation

## 1. Overview

This document outlines the simplified architectural design for the Expense Tracker Proof of
Concept (PoC) implementation. The architecture follows Django best practices with a focus on rapid
development and core functionality demonstration rather than complex patterns.

## 2. Architectural Principles

The architecture follows these key principles:

1. **Django Best Practices**: Follow Django's conventions and patterns
2. **Simplicity First**: Minimize complexity to achieve PoC goals quickly
3. **Standard Structure**: Use Django's proven app-based organization
4. **Rapid Development**: Focus on working functionality over architectural sophistication
5. **Clear Separation**: Keep models, views, and templates organized

## 3. Project Structure

```text
expense_tracker/                 # Django project root
├── manage.py
├── expense_tracker/            # Main project package
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── expenses/                   # Main Django app
│   ├── __init__.py
│   ├── admin.py               # Django admin configuration
│   ├── apps.py
│   ├── models.py              # All models
│   ├── views.py               # All views
│   ├── urls.py                # URL patterns
│   ├── forms.py               # Django forms
│   ├── templates/             # HTML templates
│   │   └── expenses/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── expense_list.html
│   │       ├── expense_form.html
│   │       └── expense_detail.html
│   └── migrations/            # Database migrations
├── static/                    # Static files
│   ├── css/
│   │   ├── base.css
│   │   └── expenses.css
│   ├── js/
│   │   └── base.js
│   └── images/
└── fixtures/                  # Test data
    ├── payees.json
    └── payment_methods.json
```

## 4. Data Models

### 4.1 Model Design

All models follow Django ORM conventions:

```python
# expenses/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Payee(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Month(models.Model):
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['year', 'month']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.year}-{self.month:02d}"
    
    def can_be_deleted(self):
        """Check if this month can be deleted (most recent with no paid items)"""
        return (
            not Month.objects.filter(
                models.Q(year__gt=self.year) |
                models.Q(year=self.year, month__gt=self.month)
            ).exists() and
            not self.expenseitem_set.filter(status='paid').exists()
        )

class Expense(models.Model):
    EXPENSE_TYPES = [
        ('endless_recurring', 'Endless Recurring'),
        ('split_payment', 'Split Payment'),
        ('one_time', 'One Time'),
    ]
    
    payee = models.ForeignKey(Payee, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True
    )
    title = models.CharField(max_length=255)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    total_amount = models.DecimalField(max_digits=13, decimal_places=2)
    installments_count = models.PositiveIntegerField(default=0)
    started_at = models.DateField()
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.payee.name}"

class ExpenseItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]
    
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.expense.title} - {self.month} - {self.status}"

class Expense(models.Model):
    # ... other fields ...
    
    def clean(self):
        """Validate expense data including start date restrictions"""
        super().clean()
        
        # Validate start date is not earlier than current month
        if self.started_at:
            from datetime import date
            today = date.today()
            current_month_start = date(today.year, today.month, 1)
            if self.started_at < current_month_start:
                raise ValidationError(
                    'Start date cannot be earlier than the current month'
                )
```

## 5. View Layer

### 5.1 View Design

Using function-based views for simplicity:

```python
# expenses/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from .models import Expense, ExpenseItem, Month, Payee, PaymentMethod
from .forms import ExpenseForm, PaymentForm

def dashboard(request):
    """Main dashboard showing current month summary"""
    current_month = get_current_month()
    pending_items = ExpenseItem.objects.filter(
        month=current_month, 
        status='pending'
    ).select_related('expense', 'expense__payee')
    
    context = {
        'current_month': current_month,
        'pending_items': pending_items,
        'total_pending': sum(item.amount for item in pending_items),
    }
    return render(request, 'expenses/dashboard.html', context)

def expense_list(request):
    """List all active expenses"""
    expenses = Expense.objects.filter(closed_at__isnull=True).select_related('payee')
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})

def expense_create(request):
    """Create new expense"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save()
            # Create items immediately if expense starts in current month
            create_initial_expense_items(expense)
            messages.success(request, 'Expense created successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm()  # Form sets default start date to current month
    
    return render(request, 'expenses/expense_form.html', {'form': form})

def month_process(request, budget_id):
    """Process new month automatically - create expense items for active expenses"""
    budget = get_object_or_404(Budget, id=budget_id)
    
    try:
        # Automatically determine next month to create
        next_allowed = Month.get_next_allowed_month(budget=budget)
        if not next_allowed:
            # Use budget start_date for initial month
            start_date = budget.start_date
            year, month = start_date.year, start_date.month
        else:
            year, month = next_allowed['year'], next_allowed['month']
        
        month_obj = process_new_month(year, month, budget)
        messages.success(request, f'Month {month_obj} processed successfully!')
        return redirect('month_detail', budget_id=budget_id, year=year, month=month)
    except Exception as e:
        messages.error(request, f'Error processing month: {str(e)}')
        return redirect('month_list', budget_id=budget_id)

def month_delete(request, year, month):
    """Delete month if it's the most recent with no paid expenses"""
    month_obj = get_object_or_404(Month, year=year, month=month)
    
    if request.method == 'POST':
        if month_obj.can_be_deleted():
            month_obj.delete()
            messages.success(request, f'Month {month_obj} deleted successfully!')
        else:
            messages.error(request, 'Cannot delete month: either not the most recent or has paid expenses')
        return redirect('month_list')
    
    return render(request, 'expenses/month_confirm_delete.html', {'month': month_obj})

def expense_item_pay(request, pk):
    """Record payment for expense item"""
    item = get_object_or_404(ExpenseItem, pk=pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            check_expense_completion(item.expense)
            messages.success(request, 'Payment recorded successfully!')
            return redirect('dashboard')
    else:
        form = PaymentForm(instance=item)
    
    return render(request, 'expenses/payment_form.html', {'form': form, 'item': item})
```

## 6. Business Logic

### 6.1 Core Functions

Business logic implemented as simple Python functions:

```python
# expenses/services.py

from datetime import date, timedelta
from django.utils import timezone
from .models import Expense, ExpenseItem, Month

def create_initial_expense_items(expense):
    """Create initial expense items based on expense type"""
    from datetime import date
    
    # Validate expense start date before creating items
    today = date.today()
    current_month_start = date(today.year, today.month, 1)
    
    # Only create items if expense starts in current month or earlier
    if expense.started_at > current_month_start:
        # Future expense - will be processed when month comes
        return
    
    current_month = get_current_month()
    
    if expense.expense_type == 'one_time':
        ExpenseItem.objects.create(
            expense=expense,
            month=current_month,
            due_date=expense.started_at,
            amount=expense.total_amount
        )
    elif expense.expense_type == 'endless_recurring':
        ExpenseItem.objects.create(
            expense=expense,
            month=current_month,
            due_date=expense.started_at,
            amount=expense.total_amount
        )
    elif expense.expense_type == 'split_payment':
        installment_amount = expense.total_amount / expense.installments_count
        ExpenseItem.objects.create(
            expense=expense,
            month=current_month,
            due_date=expense.started_at,
            amount=installment_amount
        )

def create_next_sequential_month():
    """Create the next month in sequence"""
    latest_month = Month.objects.first()  # Already ordered by -year, -month
    
    if not latest_month:
        # No months exist - create current month as seed
        today = date.today()
        return Month.objects.create(year=today.year, month=today.month)
    
    # Calculate next month
    if latest_month.month == 12:
        next_year = latest_month.year + 1
        next_month = 1
    else:
        next_year = latest_month.year
        next_month = latest_month.month + 1
    
    return Month.objects.create(year=next_year, month=next_month)

def process_monthly_expenses(month):
    """Generate expense items for active expenses in given month"""
    from datetime import date
    
    # Calculate the month date for comparison
    month_date = date(month.year, month.month, 1)
    
    # Only process expenses that have started by this month
    active_expenses = Expense.objects.filter(
        closed_at__isnull=True,
        started_at__lte=month_date
    )
    
    for expense in active_expenses:
        if expense.expense_type == 'endless_recurring':
            create_recurring_item(expense, month)
        elif expense.expense_type == 'split_payment':
            create_split_payment_item(expense, month)

def check_expense_completion(expense):
    """Check if expense should be marked as complete"""
    if expense.expense_type == 'one_time':
        paid_items = expense.expenseitem_set.filter(status='paid').count()
        if paid_items > 0:
            expense.closed_at = timezone.now()
            expense.save()
    
    elif expense.expense_type == 'split_payment':
        total_items = expense.expenseitem_set.count()
        paid_items = expense.expenseitem_set.filter(status='paid').count()
        if paid_items >= expense.installments_count:
            expense.closed_at = timezone.now()
            expense.save()
```

## 7. Frontend Architecture

### 7.1 Template Structure

Simple HTML templates with basic CSS:

```html
<!-- templates/expenses/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Expense Tracker</title>
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
</head>
<body>
    <nav>
        <a href="{% url 'dashboard' %}">Dashboard</a>
        <a href="{% url 'expense_list' %}">Expenses</a>
        <a href="{% url 'expense_create' %}">Add Expense</a>
    </nav>
    
    <main>
        {% if messages %}
            {% for message in messages %}
                <div class="message {{ message.tags }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### 7.2 Form Validation Guidelines

#### Expense Creation Form

- Default start date set to first day of current month
- Client-side validation prevents earlier dates
- Server-side validation enforces business rules
- Clear error messages for validation failures

### 7.3 CSS Guidelines

- Keep CSS simple and maintainable
- Use external stylesheets only
- No inline styles in templates
- Responsive design with basic media queries

```css
/* static/css/base.css */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}

nav {
    background: #f4f4f4;
    padding: 10px;
    margin-bottom: 20px;
}

nav a {
    margin-right: 15px;
    text-decoration: none;
    color: #333;
}

.message {
    padding: 10px;
    margin-bottom: 15px;
    border-radius: 4px;
}

.message.success {
    background: #d4edda;
    color: #155724;
}
```

## 8. Implementation Approach

### 8.1 Development Phases

#### Phase 1: Setup (Day 1)

1. Create Django project and expenses app
2. Define models and create migrations
3. Set up Django admin
4. Create fixtures for test data including initial seed month

#### Phase 2: Core Views (Days 2-3)

1. Implement basic CRUD views
2. Create simple templates
3. Add basic forms
4. Implement business logic functions

#### Phase 3: Polish (Days 4-5)

1. Add dashboard functionality
2. Improve styling
3. Add month processing
4. Test and debug

### 8.2 Testing Strategy

- Use Django's built-in testing framework
- Focus on model methods and view functionality
- Simple functional tests for core workflows

## 9. Benefits of This Approach

1. **Speed**: Rapid development using Django conventions
2. **Simplicity**: Easy to understand and maintain
3. **Flexibility**: Can easily add features or refactor
4. **Reliability**: Built on proven Django patterns
5. **Scalability**: Can evolve into more complex architecture

## 10. Future Evolution

When the PoC proves successful, the architecture can evolve to include:

- API layer for mobile apps
- More sophisticated UI framework
- Complex business logic patterns
- Advanced testing strategies
- Performance optimizations

This simplified approach allows for quick validation of core concepts while maintaining a path for future enhancement.
