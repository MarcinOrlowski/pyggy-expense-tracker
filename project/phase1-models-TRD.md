<<<<<<< HEAD
# Phase 1: Data Models Implementation

- Technical Requirements Document (TRD)
- Expense Tracker PoC - Foundation Layer
=======
# Technical Requirements Document (TRD) - Phase 1: Data Models Implementation

## Expense Tracker PoC - Foundation Layer
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

## 1. Technical Overview

### 1.1 Implementation Summary

<<<<<<< HEAD
This document details the technical implementation of Phase 1 data models for the expense tracking
system. The implementation uses Django 5.2+ ORM with SQLite database, providing a solid foundation
for the complete application.
=======
This document details the technical implementation of Phase 1 data models for the expense tracking system. The implementation uses Django 5.2+ ORM with SQLite database, providing a solid foundation for the complete application.
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

### 1.2 Technology Stack

- **Framework**: Django 5.2+
- **Database**: SQLite (development), PostgreSQL-ready
- **ORM**: Django ORM with migrations
- **Admin**: Django Admin interface
- **Python**: 3.12+

### 1.3 File Structure

<<<<<<< HEAD
```text
=======
```
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629
expenses/
├── models.py                 # Core data models (119 lines)
├── admin.py                  # Admin interface configuration (48 lines)
├── migrations/
│   └── 0001_initial.py      # Database schema migration
├── management/
│   └── commands/
│       └── setup_initial_data.py  # Data loading utility
└── apps.py                  # App configuration

fixtures/
└── initial_data.json        # Reference data fixtures

expense_tracker/
└── settings.py              # Django configuration (expenses app added)
```

## 2. Model Implementation Details

### 2.1 Base Model Patterns

<<<<<<< HEAD
#### Timestamp Pattern (Applied to All Models):
=======
**Timestamp Pattern (Applied to All Models):**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

<<<<<<< HEAD
#### Validation Pattern:
=======
**Validation Pattern:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
def clean(self):
    # Custom validation logic
    if condition:
        raise ValidationError('Error message')
```

<<<<<<< HEAD
#### String Representation:
=======
**String Representation:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
def __str__(self):
    return f"{self.field} - {self.related_field}"
```

### 2.2 Model Specifications

<<<<<<< HEAD
#### Payee Model (expenses/models.py:7-16)
=======
**Payee Model (expenses/models.py:7-16)**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
class Payee(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
```

<<<<<<< HEAD
#### Technical Details:
=======
**Technical Details:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Unique constraint on name field
- Alphabetical ordering for admin lists
- Simple string representation
- Auto-managed timestamps

<<<<<<< HEAD
#### PaymentMethod Model (expenses/models.py:19-28)
=======
**PaymentMethod Model (expenses/models.py:19-28)**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
class PaymentMethod(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
```

<<<<<<< HEAD
##### Technical Details:
=======
**Technical Details:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Identical pattern to Payee for consistency
- Unique name constraint prevents duplicates
- Optimized for dropdown selections

<<<<<<< HEAD
#### Month Model (expenses/models.py:31-46)
=======
**Month Model (expenses/models.py:31-46)**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
class Month(models.Model):
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2099)]
    )
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
```

<<<<<<< HEAD
##### Technical Details:
=======
**Technical Details:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Composite unique constraint prevents duplicate months
- Descending order (newest first)
- Range validation on year (2020-2099) and month (1-12)
- Zero-padded month display format

<<<<<<< HEAD
#### Expense Model (expenses/models.py:49-86)
=======
**Expense Model (expenses/models.py:49-86)**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
class Expense(models.Model):
    EXPENSE_TYPES = [
        ('endless_recurring', 'Endless Recurring'),
        ('split_payment', 'Split Payment'),
        ('one_time', 'One Time'),
    ]

    payee = models.ForeignKey(Payee, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    total_amount = models.DecimalField(
        max_digits=13, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    installments_count = models.PositiveIntegerField(default=0)
    started_at = models.DateField()
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.expense_type == 'split_payment' and self.installments_count <= 0:
            raise ValidationError('Split payments must have installments_count > 0')
        
        if self.expense_type in ['endless_recurring', 'one_time'] and self.installments_count > 0:
            raise ValidationError('Only split payments can have installments_count > 0')
        
        if self.closed_at and self.closed_at > timezone.now():
            raise ValidationError('closed_at cannot be in the future')

    def __str__(self):
        return f"{self.title} - {self.payee.name}"

    class Meta:
        ordering = ['-created_at']
```

<<<<<<< HEAD
##### Technical Details:
=======
**Technical Details:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Complex validation logic in clean() method
- Decimal field with 13 digits, 2 decimal places
- PROTECT delete behavior prevents payee deletion if linked to expenses
- Business rule enforcement for expense types
- Choice field for expense types with human-readable labels
- Payment method moved to ExpenseItem level for chunked payment support

<<<<<<< HEAD
#### ExpenseItem Model (expenses/models.py:89-118)
=======
**ExpenseItem Model (expenses/models.py:89-118)**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
class ExpenseItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True
    )
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(
        max_digits=13, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.status == 'paid' and not self.payment_date:
            raise ValidationError('Paid items must have payment_date')
        
        if self.status == 'pending' and self.payment_date:
            raise ValidationError('Pending items cannot have payment_date')

    def __str__(self):
        return f"{self.expense.title} - {self.month} - {self.status}"

    class Meta:
        ordering = ['due_date', '-created_at']
```

<<<<<<< HEAD
##### Technical Details:
=======
**Technical Details:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Status validation ensures data consistency
- Triple foreign key relationships (expense, month, and payment_method)
- Payment method at item level supports chunked payments with different methods
- Ordered by due date for chronological processing
- Optional payment_date field for tracking actual payments
- SET_NULL on payment method deletion preserves payment history

### 2.3 Database Schema

<<<<<<< HEAD
#### Generated Tables:
=======
**Generated Tables:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```sql
-- expenses_payee
CREATE TABLE "expenses_payee" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(255) NOT NULL UNIQUE,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- expenses_paymentmethod  
CREATE TABLE "expenses_paymentmethod" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(255) NOT NULL UNIQUE,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- expenses_month
CREATE TABLE "expenses_month" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "year" smallint unsigned NOT NULL CHECK ("year" >= 0),
    "month" smallint unsigned NOT NULL CHECK ("month" >= 0),
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- expenses_expense
CREATE TABLE "expenses_expense" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" varchar(255) NOT NULL,
    "expense_type" varchar(20) NOT NULL,
    "total_amount" decimal NOT NULL,
    "installments_count" integer unsigned NOT NULL CHECK ("installments_count" >= 0),
    "started_at" date NOT NULL,
    "closed_at" datetime NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "payee_id" bigint NOT NULL REFERENCES "expenses_payee" ("id") ON DELETE PROTECT
);

-- expenses_expenseitem
CREATE TABLE "expenses_expenseitem" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "due_date" date NOT NULL,
    "payment_date" date NULL,
    "amount" decimal NOT NULL,
    "status" varchar(10) NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "expense_id" bigint NOT NULL REFERENCES "expenses_expense" ("id") DEFERRABLE INITIALLY DEFERRED,
    "month_id" bigint NOT NULL REFERENCES "expenses_month" ("id") DEFERRABLE INITIALLY DEFERRED,
    "payment_method_id" bigint NULL REFERENCES "expenses_paymentmethod" ("id") ON DELETE SET NULL
);
```

<<<<<<< HEAD
#### Indexes:
=======
**Indexes:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Primary keys on all tables (auto-generated)
- Unique constraints on payee.name, paymentmethod.name
- Unique constraint on month(year, month)
- Foreign key indexes (auto-generated by Django)

## 3. Admin Interface Implementation

### 3.1 Admin Configuration (expenses/admin.py:1-48)

<<<<<<< HEAD
#### Performance Optimizations:
=======
**Performance Optimizations:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
def get_queryset(self, request):
    return super().get_queryset(request).select_related('payee', 'payment_method')
```

<<<<<<< HEAD
#### Common Admin Features:
=======
**Common Admin Features:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- `list_display`: Key fields shown in list view
- `search_fields`: Searchable fields for quick filtering
- `list_filter`: Sidebar filters for data segmentation
- `readonly_fields`: Prevent modification of timestamps
- `date_hierarchy`: Date-based navigation

<<<<<<< HEAD
#### ExpenseAdmin Specifics:
=======
**ExpenseAdmin Specifics:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Select related queries prevent N+1 problems
- Date hierarchy on started_at for temporal navigation
- Comprehensive filtering by type, status, and payee
- No longer includes payment_method (moved to ExpenseItem level)

<<<<<<< HEAD
#### ExpenseItemAdmin Specifics:
=======
**ExpenseItemAdmin Specifics:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Quadruple select_related for optimal query performance (expense/payee/month/payment_method)
- Status-based filtering for payment management
- Payment method filtering for payment analysis
- Date hierarchy on due_date for payment scheduling

### 3.2 Query Optimization

<<<<<<< HEAD
#### Select Related Usage:
=======
**Select Related Usage:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
# ExpenseAdmin
.select_related('payee')

# ExpenseItemAdmin  
.select_related('expense', 'expense__payee', 'month', 'payment_method')
```

<<<<<<< HEAD
#### Benefits:
=======
**Benefits:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Reduces database queries from O(n) to O(1)
- Improves admin interface response times
- Prevents performance degradation with large datasets

## 4. Data Management Implementation

### 4.1 Initial Data Fixtures (fixtures/initial_data.json)

<<<<<<< HEAD
#### Structure:
=======
**Structure:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```json
[
  {
    "model": "expenses.payee",
    "pk": 1,
    "fields": {
      "name": "Electric Company",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  }
]
```

<<<<<<< HEAD
#### Content:
=======
**Content:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- 5 sample payees (utility companies, services)
- 5 payment methods (cards, transfer, cash, digital)
- Consistent timestamps for clean data

### 4.2 Management Command (expenses/management/commands/setup_initial_data.py)

<<<<<<< HEAD
#### Implementation:
=======
**Implementation:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
def handle(self, *args, **options):
    self.stdout.write(self.style.SUCCESS('Loading initial data...'))
    
    try:
        call_command('loaddata', 'fixtures/initial_data.json')
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded initial data!')
        )
    except Exception as e:
        self.stdout.write(
            self.style.ERROR(f'Error loading initial data: {e}')
        )
```

<<<<<<< HEAD
#### Features:
=======
**Features:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Error handling with user feedback
- Django command framework integration
- Colored output for success/error states
- Safe to run multiple times (Django handles duplicates)

## 5. Database Migration Details

### 5.1 Migration File (expenses/migrations/0001_initial.py)

<<<<<<< HEAD
#### Generated Operations:
=======
**Generated Operations:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

1. Create model Expense
2. Create model Payee  
3. Create model PaymentMethod
4. Create model Month
5. Create model ExpenseItem
6. Add field payee to expense
7. Add field payment_method to expense

<<<<<<< HEAD
#### Dependencies:
=======
**Dependencies:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Django built-in migrations (auth, contenttypes)
- No custom dependencies required

### 5.2 Migration Execution Results

<<<<<<< HEAD
#### Tables Created:
=======
**Tables Created:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- `expenses_payee` (4 fields)
- `expenses_paymentmethod` (4 fields)
- `expenses_month` (5 fields with constraints)
- `expenses_expense` (10 fields with relationships)
- `expenses_expenseitem` (9 fields with dual relationships)

<<<<<<< HEAD
#### Constraints Applied:
=======
**Constraints Applied:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Unique constraints on names
- Foreign key constraints with proper cascading
- Check constraints on numeric ranges
- NOT NULL constraints where required

## 6. Testing and Validation

### 6.1 Model Validation Testing

<<<<<<< HEAD
#### Test Commands Executed:
=======
**Test Commands Executed:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```bash
# System check
python manage.py check
# Result: System check identified no issues (0 silenced)

# Shell testing
python manage.py shell
# Created test data successfully
# Verified relationships work correctly
# Confirmed validation rules prevent invalid data
```

<<<<<<< HEAD
#### Validation Scenarios Tested:
=======
**Validation Scenarios Tested:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Split payment with installments_count = 0 (rejected)
- One-time payment with installments_count > 0 (rejected)
- Paid item without payment_date (rejected)
- Pending item with payment_date (rejected)
- Future closed_at date (rejected)

### 6.2 Data Integrity Verification

<<<<<<< HEAD
#### Database State After Setup:
=======
**Database State After Setup:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- 5 Payees loaded successfully
- 5 Payment Methods loaded successfully
- 1 Test month created (2024-12)
- 1 Test expense created successfully
- All relationships functioning properly

<<<<<<< HEAD
#### Performance Verification:
=======
**Performance Verification:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Admin interface loads quickly
- Search functionality responsive
- Filtering operations efficient
- Select related queries optimized

## 7. Configuration Requirements

### 7.1 Django Settings Updates

<<<<<<< HEAD
#### INSTALLED_APPS Addition:
=======
**INSTALLED_APPS Addition:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'expenses',  # Added for Phase 1
]
```

### 7.2 Dependencies (requirements.txt)

<<<<<<< HEAD
#### Core Requirements:

```text
=======
**Core Requirements:**

```
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629
Django>=5.2.1
asgiref>=3.8.1
sqlparse>=0.5.2
tzdata>=2024.2
```

<<<<<<< HEAD
#### Environment Setup:
=======
**Environment Setup:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Python 3.12+ virtual environment
- SQLite database (no additional setup required)
- Django development server

## 8. Security and Performance Considerations

### 8.1 Data Protection

<<<<<<< HEAD
#### Model-Level Security:
=======
**Model-Level Security:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Validation prevents SQL injection via ORM
- Field length limits prevent buffer overflow
- Numeric constraints prevent invalid values
- Timestamp automation prevents manipulation

<<<<<<< HEAD
#### Admin Interface Security:
=======
**Admin Interface Security:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Requires Django authentication
- Built-in CSRF protection
- Permission-based access control
- Audit trail via timestamps

### 8.2 Performance Optimization

<<<<<<< HEAD
#### Database Performance:
=======
**Database Performance:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Appropriate field types for data size
- Indexes on frequently queried fields
- Select related for relationship queries
- Efficient ordering specifications

<<<<<<< HEAD
#### Memory Management:
=======
**Memory Management:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Minimal field sizes where appropriate
- Efficient string representations
- Optimized admin querysets
- Lazy loading of related objects

## 9. Future Integration Points

### 9.1 Business Logic Preparation

<<<<<<< HEAD
#### Ready for Phase 2:
=======
**Ready for Phase 2:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Models support all three expense types
- Validation framework in place
- Admin interface for testing business logic
- Database structure supports monthly processing

<<<<<<< HEAD
#### Extension Hooks:
=======
**Extension Hooks:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Model methods can be added for business logic
- Custom managers for complex queries
- Signal handlers for automatic processing
- Additional validation rules as needed

### 9.2 API Readiness

<<<<<<< HEAD
#### Model Structure:
=======
**Model Structure:**
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

- Serialization-friendly field types
- Clear relationship definitions
- Comprehensive validation rules
- RESTful resource mapping potential

This Phase 1 implementation provides a robust, well-tested foundation for the expense tracking system. All models are properly implemented with Django best practices, comprehensive validation, and optimized performance characteristics.
