# Technical Requirements Document (TRD)

## 1. Overview

This Technical Requirements Document defines the specific technical implementation details
for the Expense Tracker Proof of Concept. It complements the PRD and Architecture Specification
by providing concrete technical specifications, constraints, and implementation guidelines.

## 2. Technology Stack

### 2.1 Core Technologies

#### Backend Framework

- Python 3.12+
- Django 4.2+ (LTS)
- Django ORM for database operations

#### Database

- SQLite for development and PoC
- PostgreSQL ready (future production)

#### Frontend

- HTML5 semantic markup
- CSS3 with Flexbox/Grid (processed via build tools)
- Vanilla JavaScript (ES6+)
- Vite for fast development and bundling
- PostCSS for CSS processing and autoprefixing

#### Development Tools

- Django development server
- Django admin interface
- Django management commands
- Python virtual environment
- Vite dev server for frontend assets
- Hot module replacement for CSS/JS
- Automated CSS minification and bundling

### 2.2 Dependencies

#### Required Python Packages

```python
Django>=4.2,<5.0
python-decouple>=3.8    # Environment configuration
django-extensions>=3.2  # Development utilities
django-vite>=2.0        # Vite integration for Django
```

#### Frontend Build Tools

```json
{
  "devDependencies": {
    "vite": "^5.0.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "cssnano": "^6.0.0"
  }
}
```

#### Optional Development Packages

```python
django-debug-toolbar>=4.0  # Debug information
black>=23.0                # Code formatting
flake8>=6.0               # Code linting
pytest-django>=4.5       # Testing framework
```

## 3. Database Requirements

### 3.1 Database Schema

#### User Model

- Uses Django's built-in `django.contrib.auth.models.User`
- No customization required for PoC
- Authentication handled by Django admin

#### Core Models with Constraints

```sql
-- Payee Table
CREATE TABLE expenses_payee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- PaymentMethod Table  
CREATE TABLE expenses_paymentmethod (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Month Table
CREATE TABLE expenses_month (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL CHECK (year >= 2020 AND year <= 2099),
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE(year, month)
);

-- Business constraints (enforced in application logic):
-- 1. System must be seeded with initial month
-- 2. New months must be created sequentially
-- 3. Can only delete most recent month if no paid expenses exist

-- Expense Table
CREATE TABLE expenses_expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payee_id INTEGER NOT NULL REFERENCES expenses_payee(id) ON DELETE CASCADE,
    payment_method_id INTEGER REFERENCES expenses_paymentmethod(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    expense_type VARCHAR(20) NOT NULL CHECK (
        expense_type IN ('endless_recurring', 'split_payment', 'one_time')
    ),
    total_amount DECIMAL(13,2) NOT NULL CHECK (total_amount > 0),
    installments_count INTEGER NOT NULL DEFAULT 0 CHECK (installments_count >= 0),
    started_at DATE NOT NULL,
    closed_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    -- Business rule constraints
    CHECK (
        (expense_type = 'split_payment' AND installments_count > 0) OR
        (expense_type IN ('endless_recurring', 'one_time') AND installments_count = 0)
    ),
    CHECK (closed_at IS NULL OR closed_at >= created_at)
);

-- ExpenseItem Table
CREATE TABLE expenses_expenseitem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER NOT NULL REFERENCES expenses_expense(id) ON DELETE CASCADE,
    month_id INTEGER NOT NULL REFERENCES expenses_month(id) ON DELETE CASCADE,
    due_date DATE NOT NULL,
    payment_date DATE NULL,
    amount DECIMAL(13,2) NOT NULL CHECK (amount > 0),
    status VARCHAR(10) NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'paid')
    ),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    -- Business rule constraints
    CHECK (
        (status = 'paid' AND payment_date IS NOT NULL) OR
        (status = 'pending' AND payment_date IS NULL)
    ),
    CHECK (payment_date IS NULL OR payment_date >= due_date OR payment_date >= DATE('2020-01-01'))
);

-- Indexes for performance
CREATE INDEX idx_expense_type ON expenses_expense(expense_type);
CREATE INDEX idx_expense_active ON expenses_expense(closed_at) WHERE closed_at IS NULL;
CREATE INDEX idx_expenseitem_status ON expenses_expenseitem(status);
CREATE INDEX idx_expenseitem_month ON expenses_expenseitem(month_id);
CREATE INDEX idx_month_lookup ON expenses_month(year, month);
```

### 3.2 Data Integrity Rules

#### Model-Level Validation

```python
# In models.py
class Expense(models.Model):
    def clean(self):
        # Validate split payment has installments
        if self.expense_type == 'split_payment' and self.installments_count <= 0:
            raise ValidationError('Split payments must have installments_count > 0')
        
        # Validate non-split payments have no installments
        if self.expense_type in ['endless_recurring', 'one_time'] and self.installments_count > 0:
            raise ValidationError('Only split payments can have installments_count > 0')
        
        # Validate closed_at is not in future
        if self.closed_at and self.closed_at > timezone.now():
            raise ValidationError('closed_at cannot be in the future')

class ExpenseItem(models.Model):
    def clean(self):
        # Validate payment date matches status
        if self.status == 'paid' and not self.payment_date:
            raise ValidationError('Paid items must have payment_date')
        
        if self.status == 'pending' and self.payment_date:
            raise ValidationError('Pending items cannot have payment_date')
```

### 3.3 Database Performance

#### Required Indexes

- Foreign key indexes (automatic in Django)
- Composite index on Month(year, month)
- Index on Expense.closed_at for active expense queries
- Index on ExpenseItem.status for pending/paid queries

#### Query Optimization

- Use select_related() for foreign key relationships
- Use prefetch_related() for reverse foreign key queries
- Limit querysets with appropriate filtering

## 4. API Specifications

### 4.1 URL Structure

```python
# Main URLs (expense_tracker/urls.py)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('expenses.urls')),
]

# App URLs (expenses/urls.py)
urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Expense Management
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Month Processing
    path('months/', views.month_list, name='month_list'),
    path('months/<int:year>/<int:month>/', views.month_detail, name='month_detail'),
    path('months/process/', views.month_process, name='month_process'),
    
    # Payment Processing
    path('expense-items/<int:pk>/pay/', views.expense_item_pay, name='expense_item_pay'),
    path('expense-items/<int:pk>/unpay/', views.expense_item_unpay, name='expense_item_unpay'),
    
    # Reference Data
    path('payees/', views.payee_list, name='payee_list'),
    path('payment-methods/', views.payment_method_list, name='payment_method_list'),
]
```

### 4.2 View Specifications

#### Function Signatures

```python
def dashboard(request) -> HttpResponse:
    """Display current month summary with pending payments"""

def expense_list(request) -> HttpResponse:
    """List active expenses with filtering options"""

def expense_create(request) -> HttpResponse:
    """Create new expense with form validation"""

def expense_detail(request, pk: int) -> HttpResponse:
    """Display expense details and related items"""

def expense_edit(request, pk: int) -> HttpResponse:
    """Edit existing expense"""

def expense_delete(request, pk: int) -> HttpResponse:
    """Delete expense with confirmation"""

def month_process(request) -> HttpResponse:
    """Process new month generation"""

def expense_item_pay(request, pk: int) -> HttpResponse:
    """Record payment for expense item"""
```

### 4.3 Form Specifications

#### ExpenseForm

```python
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['payee', 'payment_method', 'title', 'expense_type', 
                 'total_amount', 'installments_count', 'started_at']
        widgets = {
            'started_at': forms.DateInput(attrs={'type': 'date'}),
            'expense_type': forms.Select(attrs={'id': 'expense-type-select'}),
            'installments_count': forms.NumberInput(attrs={'min': '0'}),
            'total_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
        }
    
    def clean(self):
        # Custom validation logic
        pass
```

#### PaymentForm

```python
class PaymentForm(forms.ModelForm):
    class Meta:
        model = ExpenseItem
        fields = ['payment_date', 'status']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }
```

## 5. Business Logic Requirements

### 5.1 Core Services

#### Monthly Processing Service

```python
# expenses/services.py

def process_new_month(year: int, month: int) -> Month:
    """
    Create new month and generate expense items for active expenses.
    
    Args:
        year: Target year (2020-2099)
        month: Target month (1-12)
        
    Returns:
        Month: Created or existing month instance
        
    Raises:
        ValidationError: If month already processed or not sequential
        ValueError: If invalid year/month
        
    Business Rules:
    - Must have at least one existing month (initial seed month)
    - New month must be exactly one month after the most recent month
    - Cannot create months out of sequence
    """

def can_delete_month(month: Month) -> bool:
    """
    Check if a month can be deleted.
    
    Rules:
    - Must be the most recent month
    - Must have no paid expense items
    """
    # Check if this is the most recent month
    if Month.objects.filter(
        models.Q(year__gt=month.year) | 
        models.Q(year=month.year, month__gt=month.month)
    ).exists():
        return False
    
    # Check for paid expenses
    return not ExpenseItem.objects.filter(
        month=month, 
        status='paid'
    ).exists()

def create_expense_items_for_month(expense: Expense, month: Month) -> List[ExpenseItem]:
    """
    Generate appropriate expense items for given expense and month.
    
    Business Rules:
    - endless_recurring: Create one item per month
    - split_payment: Create items until installments_count reached
    - one_time: Create single item only in start month
    - Only create items if expense has started (started_at <= current month)
    """

def validate_expense_start_date(expense: Expense) -> bool:
    """
    Validate that expense start date is not earlier than current month.
    
    Args:
        expense: Expense instance to validate
        
    Returns:
        bool: True if valid, raises ValidationError if invalid
        
    Raises:
        ValidationError: If start date is before current month
    """
    from datetime import date
    from django.core.exceptions import ValidationError
    
    today = date.today()
    current_month_start = date(today.year, today.month, 1)
    
    if expense.started_at < current_month_start:
        raise ValidationError(
            f'Expense start date {expense.started_at} cannot be earlier than '
            f'current month {current_month_start}'
        )
    return True

def calculate_installment_amount(expense: Expense) -> Decimal:
    """Calculate per-installment amount for split payments."""
    return expense.total_amount / expense.installments_count

def check_expense_completion(expense: Expense) -> bool:
    """
    Check if expense should be marked as complete.
    
    Rules:
    - one_time: Complete when single item is paid
    - split_payment: Complete when all installments paid
    - endless_recurring: Manual completion only
    """
```

### 5.2 Data Validation Rules

#### Expense Creation Rules

1. Split payments must have installments_count > 0
2. Other expense types must have installments_count = 0
3. total_amount must be > 0
4. started_at cannot be in future beyond reasonable limit (1 year)

#### Payment Recording Rules

1. Can only pay pending expense items
2. Payment date cannot be before due date (with grace period)
3. Payment date cannot be in future
4. Status and payment_date must be consistent

#### Month Processing Rules

1. System must be initialized with a seed month (e.g., 2025-01)
2. Cannot process same month twice
3. Must process months in strict chronological order (no gaps)
4. Can only create the next sequential month after the most recent
5. Only create items for expenses that have started

#### Month Deletion Rules

1. Can only delete the most recent month in the system
2. Cannot delete if any expense items in that month are paid
3. Deletion cascades to remove all pending expense items

## 6. Security Requirements

### 6.1 Authentication & Authorization

#### For PoC (Simplified)

- Use Django's built-in authentication
- Single-user system (admin user)
- All access through Django admin login
- No public registration

#### Session Management

- Django's default session handling
- Session timeout: 2 weeks (Django default)
- CSRF protection enabled
- Secure cookie settings for production

### 6.2 Input Validation

#### Form Validation

- All user inputs validated via Django forms
- Decimal fields with appropriate precision limits
- Date fields with reasonable ranges
- Text fields with length limits

#### SQL Injection Prevention

- Django ORM handles parameterized queries
- No raw SQL in PoC
- All database access through Django models

### 6.3 Data Protection

#### Sensitive Data

- No sensitive financial data in PoC
- No PII beyond basic expense descriptions
- Local SQLite database (not exposed)

## 7. Performance Requirements

### 7.1 Response Time Targets

#### Page Load Times (PoC Targets)

- Dashboard: < 500ms
- Expense list: < 1s
- Expense create/edit: < 300ms
- Month processing: < 2s

### 7.2 Database Performance

#### Query Limits

- Maximum 10 database queries per page load
- Use select_related/prefetch_related for relationships
- Pagination for lists > 50 items

#### Database Size Limits (PoC)

- SQLite file size < 100MB
- Maximum 10,000 expense items
- Maximum 100 active expenses

### 7.3 Memory Usage

#### Development Server

- Memory usage < 200MB
- Django debug mode acceptable for PoC

## 8. Testing Requirements

### 8.1 Testing Strategy

#### Unit Tests

```python
# Test model validation
def test_expense_validation():
    # Test split payment validation
    # Test amount validation
    # Test date validation

# Test business logic
def test_monthly_processing():
    # Test expense item generation
    # Test completion checking
    
# Test forms
def test_expense_form_validation():
    # Test valid/invalid inputs
```

#### Integration Tests

```python
def test_expense_creation_workflow():
    # End-to-end expense creation
    
def test_payment_recording_workflow():
    # End-to-end payment process
```

### 8.2 Test Coverage Targets

- Model methods: 90%+
- Business logic functions: 90%+
- Views: 70%+
- Forms: 80%+

### 8.3 Test Data

#### Fixtures Required

```python
# fixtures/test_data.json
[
    {
        "model": "expenses.payee",
        "fields": {"name": "Electric Company"}
    },
    {
        "model": "expenses.paymentmethod", 
        "fields": {"name": "Credit Card"}
    }
]
```

## 9. Deployment Requirements

### 9.1 Development Environment

#### Setup Steps

```bash
# Python environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend dependencies
npm install

# Django setup
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata fixtures/initial_data.json

# Development servers (run in separate terminals)
npm run dev        # Vite dev server with HMR
python manage.py runserver  # Django server
```

#### Environment Variables

```bash
# .env file
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
VITE_DEV_MODE=True
```

#### Build Configuration Files

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: '/static/',
  build: {
    outDir: 'static',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'frontend/js/base.js'),
        styles: resolve(__dirname, 'frontend/css/base.css')
      }
    }
  },
  server: {
    host: 'localhost',
    port: 3000,
    open: false
  }
});
```

```javascript
// postcss.config.js
module.exports = {
  plugins: {
    autoprefixer: {},
    cssnano: process.env.NODE_ENV === 'production' ? {} : false
  }
};
```

```json
// package.json scripts
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

### 9.2 Production Considerations (Future)

#### Database Migration

- SQLite → PostgreSQL migration script
- Data backup procedures
- Database connection pooling

#### Security Hardening

- HTTPS enforcement
- Security headers
- Database credential management
- Static file serving

## 10. Monitoring & Logging

### 10.1 Logging Requirements

#### Log Levels

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'expense_tracker.log',
        },
    },
    'loggers': {
        'expenses': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

#### Events to Log

- Expense creation/modification/deletion
- Monthly processing execution
- Payment recording
- Error conditions

### 10.2 Error Handling

#### Exception Handling Strategy

```python
# Custom exception classes
class ExpenseTrackerError(Exception):
    """Base exception for expense tracker"""

class MonthProcessingError(ExpenseTrackerError):
    """Raised when month processing fails"""

class PaymentRecordingError(ExpenseTrackerError):
    """Raised when payment recording fails"""
```

## 11. Data Migration & Backup

### 11.1 Data Fixtures

#### Initial Data

```python
# management/commands/setup_initial_data.py
def handle(self):
    # Create default payees
    # Create default payment methods
    # Create initial seed month (required for system operation)
    from datetime import date
    current_date = date.today()
    Month.objects.get_or_create(
        year=current_date.year,
        month=current_date.month
    )
```

### 11.2 Backup Strategy (PoC)

#### Development Backup

- SQLite file backup before major changes
- Fixture export for data preservation
- Git repository for code versioning

## 12. Compliance & Standards

### 12.1 Code Standards

#### Python Code Style

- PEP 8 compliance
- Black formatting
- Type hints where beneficial
- Docstrings for public methods

#### Django Best Practices

- Model validation in clean() methods
- Form validation for user input
- URL naming conventions
- Template organization

### 12.2 Documentation Standards

#### Code Documentation

- Docstrings for all models, views, and services
- Inline comments for complex business logic
- README with setup instructions
- API documentation for endpoints

## 13. Build Tools Benefits

### 13.1 Why Vite + PostCSS?

#### Development Benefits

- **Hot Module Replacement**: Instant CSS/JS updates without page refresh
- **Fast Build Times**: Vite's esbuild-powered bundling is 10-100x faster than webpack
- **Modern Browser Features**: Native ES modules in development
- **Automatic Browser Prefixing**: PostCSS autoprefixer handles vendor prefixes
- **CSS Optimization**: Automatic minification and duplicate removal

#### Production Benefits

- **Optimized Bundles**: Tree-shaking removes unused code
- **Asset Hashing**: Automatic cache-busting for deployments
- **CSS Purging**: Remove unused CSS classes automatically
- **Gzip Compression**: Smaller file sizes for faster loading

#### Developer Experience

- **Zero Configuration**: Works out of the box with sensible defaults
- **Error Overlay**: Clear error messages during development
- **Source Maps**: Debug original source in production builds
- **Modern Syntax**: Use latest CSS and JS features with automatic transpilation

### 13.2 Development Workflow

```bash
# Start development (two terminals)
Terminal 1: npm run dev          # Vite dev server (localhost:3000)
Terminal 2: python manage.py runserver  # Django server (localhost:8000)

# Build for production
npm run build                    # Creates optimized static files
python manage.py collectstatic   # Django collects all static files
```

#### File Structure with Build Tools

- `frontend/` - Source files (editable)
- `static/` - Built files (auto-generated, don't edit)
- Hot reloading updates `static/` automatically during development

This TRD provides the technical foundation for implementing the Expense Tracker PoC with modern build tools that enhance development speed and production performance while maintaining the simplified Django approach.
