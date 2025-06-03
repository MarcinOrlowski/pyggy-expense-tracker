# Product Requirements Document (PRD) - Expense Tracker and Budget Management System - PoC Version

## 1. Project Overview

### 1.1 Purpose

Develop a focused proof-of-concept (PoC) expense tracking application using Python 3.12 and Django. The PoC will demonstrate the core expense tracking functionality, particularly the handling of different expense types and monthly processing, as a foundation for a more comprehensive system in future phases.

### 1.2 Technology Stack

- Python 3.12
- Django framework
- SQLite database for development
- Simple HTML/CSS frontend (no complex build tools)
- Django built-in admin for initial data management

### 1.3 PoC Objectives

- Demonstrate core expense tracking functionality
- Support various expense types (recurring, installment-based, one-time)
- Implement monthly expense item generation
- Create basic expense management interface
- Simple, fast development focused on core business logic

## 2. Core Requirements

### 2.1 Expense Types

The system must support three fundamental expense types:

1. **Endless Recurring Payments**
   - Monthly recurring expenses without a defined end date (e.g., utilities, subscriptions)
   - Automatically generated each month until manually closed

2. **Split Payments**
   - Fixed number of installments (e.g., loans, payment plans)
   - System tracks which installment is current and total remaining
   - Automatically marks expense as complete after final installment

3. **One-time Payments**
   - Single payment expenses (e.g., individual purchases)
   - Automatically closed after payment

### 2.2 Monthly Processing

- The system must be seeded with an initial month (e.g., 2025-01) during setup
- Month creation rules:
  - Users can only add new months sequentially (next month after the most recent)
  - Cannot skip months or create months out of order
  - Cannot create duplicate months
- Month deletion rules:
  - Users can only delete the most recent month
  - Cannot delete a month if it has any paid expenses
  - Once any expense is paid in a month, that month is locked and cannot be deleted
- At month creation, the system should:
  - Auto-populate with the next installment of all active endless recurring expenses
  - Auto-populate with the next installment of all active split payment expenses
- Ability to record payments for expense items
- Basic monthly view showing all expenses for selected month

### 2.3 Expense Creation

- Users can create new expenses of any type at any time
- **Start Date Validation Rules:**
  - Expense start dates cannot be earlier than the current month
  - Default start date in forms is set to the current month's first day
  - If an expense starts in the current month, expense items are created immediately
  - Future expenses will be processed when their month comes
- For expenses with current month start dates, automatically create initial ExpenseItem

### 2.4 Expense Completion

- Split payments are automatically marked complete after final installment
- Endless recurring payments can be manually marked complete when no longer active
- Completed expenses are retained but filtered from active views
- Completion is tracked via a 'closed_at' timestamp

## 3. Entity Structure (Simplified for PoC)

### 3.1 Django Models

**User**

- Uses Django's built-in User model
- No customization needed for PoC

**Payee**

```python
class Payee(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**PaymentMethod**

```python
class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Expense**

```python
class Expense(models.Model):
    EXPENSE_TYPES = [
        ('endless_recurring', 'Endless Recurring'),
        ('split_payment', 'Split Payment'),
        ('one_time', 'One Time'),
    ]
    
    payee = models.ForeignKey(Payee, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    total_amount = models.DecimalField(max_digits=13, decimal_places=2)
    installments_count = models.PositiveIntegerField(default=0)
    started_at = models.DateField()
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**ExpenseItem**

```python
class ExpenseItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]
    
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    month = models.ForeignKey('Month', on_delete=models.CASCADE)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Month**

```python
class Month(models.Model):
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['year', 'month']
        
    # Business rules:
    # - Must be seeded with initial month during system setup
    # - New months can only be created sequentially
    # - Deletion only allowed for most recent month with no paid expenses
```

## 4. System Workflows

### 4.1 New Month Process

1. Validate month creation is allowed:
   - Check that previous month exists (or this is the initial month)
   - Ensure the new month is the next sequential month
   - Prevent duplicate month creation
2. Create new Month record
3. For each active expense:
   - Generate ExpenseItem for endless recurring expenses
   - Generate next ExpenseItem for split payments not yet completed
   - Set appropriate due dates

### 4.2 New Expense Creation

1. Create main Expense record
2. Generate initial ExpenseItem(s) based on expense type
3. Link to appropriate Month based on started_at

### 4.3 Payment Recording

1. Update ExpenseItem when payment is made
2. Record actual payment amount and date
3. For split payments, check if final installment and mark Expense as closed if completed

### 4.4 Expense Completion

1. Set closed_at timestamp when expense is completed
2. For split payments, this can be automated when final installment is paid
3. For endless recurring, this is manual when service is canceled

## 5. User Interface Requirements (Simplified for PoC)

### 5.1 Dashboard

- Monthly overview with total expenses
- Upcoming payments list
- Quick expense entry

### 5.2 Expense Management

- List view with basic filtering options
- Create/edit forms for expenses
- Payment recording interface

### 5.3 Monthly View

- Simple calendar or list view of expenses by month
- Month navigation controls

## 6. Technical Implementation Notes

### 6.1 Django Implementation

**Database**

- Use Django ORM with SQLite for simplicity
- Django migrations handle schema creation
- No complex database optimizations for PoC

**Views (Simplified)**

```python
# Function-based views for quick development
def expense_list(request):          # List expenses
def expense_create(request):        # Create expense
def expense_detail(request, pk):    # View/edit expense
def expense_delete(request, pk):    # Delete expense

def month_process(request):         # Process new month
def expense_item_pay(request, pk):  # Record payment

def dashboard(request):             # Main dashboard
```

**URL Structure**

```python
# Simple URL patterns
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('months/process/', views.month_process, name='month_process'),
    path('expense-items/<int:pk>/pay/', views.expense_item_pay, name='expense_item_pay'),
]
```

### 6.3 Business Logic Clarification

1. **Endless Recurring Expenses**
   - Generate a new ExpenseItem each month with the same amount
   - Due date will be the same day of month as the original started_at date
   - Monthly generation continues until expense is manually closed

2. **Split Payment Expenses**
   - Require installments_count > 0 and total_amount
   - Each installment amount equals total_amount / installments_count
   - Generate ExpenseItems up to installments_count
   - Automatically close expense after final installment is paid

3. **One-time Expenses**
   - Create a single ExpenseItem with amount equal to total_amount
   - Automatically close expense when ExpenseItem is paid

4. **Monthly Processing Rules**
   - System must be initialized with a starting month (e.g., 2025-01)
   - Month records can only be created sequentially (no gaps or out-of-order creation)
   - New month process generates the next installment for all active endless recurring and split payment expenses
   - ExpenseItems are created with status='pending'
   - When recording payment, status changes to 'paid' and payment_date is set
   - Months with paid expenses cannot be deleted (data integrity protection)
   - Only the most recent month can be deleted, and only if it has no paid expenses

5. **Expense Start Date Rules**
   - Expenses cannot be created with start dates earlier than the current month
   - This prevents creating historical data that would require complex retroactive processing
   - Form default behavior sets start date to first day of current month for user convenience
   - Validation ensures data integrity and maintains chronological consistency
   - Future-dated expenses are allowed to support planning ahead

## 7. Implementation Plan for PoC

### Phase 1: Foundation (1-2 days)

1. Set up Django project
2. Create models and migrations
3. Set up Django admin
4. Create fixtures for reference data (payees, payment methods)
5. Basic project structure

### Phase 2: Core Functionality (2-3 days)

1. Implement basic views for expense CRUD
2. Create simple templates with minimal CSS
3. Build monthly processing function
4. Create expense item payment recording
5. Implement expense completion logic

### Phase 3: UI Polish (1-2 days)

1. Create dashboard view
2. Add basic navigation
3. Improve form handling
4. Add simple styling
5. Month navigation functionality

**Total Timeline: ~1 week**

Note: Authentication uses Django's built-in system. Initial focus on functionality over UI polish.

## 8. Future Enhancements (Post-PoC)

### 8.1 Multi-Project Support

- Allow users to create and manage multiple financial projects
- Project selection and switching
- Project-specific data isolation

### 8.2 Budget Management

- Monthly budget setting and tracking
- Budget vs. actual comparison reports
- Budget category management

### 8.3 Enhanced Payee & Payment Method Management

- Full CRUD operations for payees and payment methods
- Active/inactive status management
- Additional payee details (website, notes, etc.)

### 8.4 Advanced Features

- Tags and categorization
- Advanced reporting and analytics
- Receipt image storage
- Multi-user access to projects
- Mobile application
- Export/import functionality
- Notification system for upcoming payments
- Bank statement import/reconciliation
