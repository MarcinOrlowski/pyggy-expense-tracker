# Phase 1: Data Models Implementation

- Product Requirements Document (PRD)
- Expense Tracker PoC - Foundation Layer

## 1. Phase Overview

### 1.1 Purpose

Implement the foundational data models and database layer for the expense tracking system. This
phase establishes the core data structures that will support all future functionality, focusing on
proper relationships, validation, and data integrity.

### 1.2 Scope

- Core database models for expense tracking
- Django ORM implementation with proper validation
- Database migrations and schema creation
- Admin interface for data management
- Initial data fixtures and setup utilities

### 1.3 Success Criteria

- ✅ All core models implemented with proper relationships
- ✅ Database schema created with appropriate constraints
- ✅ Data validation rules enforced at model level
- ✅ Admin interface functional for all models
- ✅ Initial data can be loaded successfully
- ✅ Models support the three expense types defined in main PRD

## 2. Data Model Requirements

### 2.1 Core Entities

#### Payee Model

- Purpose: Store vendor/company information for expenses
- Fields:
  - `name`: Unique company/vendor name (CharField, max 255, unique)
  - `created_at`: Automatic timestamp (DateTimeField)
  - `updated_at`: Automatic timestamp (DateTimeField)
- Business Rules:
  - Names must be unique across the system
  - Deletion is PROTECTED - cannot delete payee if linked to any expenses
  - Alphabetical ordering by default

#### PaymentMethod Model

- Purpose: Track different payment types (Credit Card, Cash, etc.)
- Fields:
  - `name`: Unique payment method name (CharField, max 255, unique)
  - `created_at`: Automatic timestamp (DateTimeField)
  - `updated_at`: Automatic timestamp (DateTimeField)
- Business Rules:
  - Names must be unique across the system
  - Can be removed from expense items (SET_NULL on delete)
  - Alphabetical ordering by default

#### Month Model

- Purpose: Organize expenses by month/year for processing
- Fields:
  - `year`: Year value (PositiveSmallIntegerField, 2020-2099)
  - `month`: Month value (PositiveSmallIntegerField, 1-12)
  - `created_at`: Automatic timestamp (DateTimeField)
  - `updated_at`: Automatic timestamp (DateTimeField)
- Business Rules:
  - Unique combination of year and month
  - Ordered by year/month descending (most recent first)
  - System must be seeded with an initial month during setup
  - New months can only be created sequentially (next month after most recent)
  - Cannot skip months or create out of order
  - Can only delete the most recent month if it has no paid expenses
  - Once any expense is paid in a month, that month is locked

#### Expense Model

- Purpose: Main expense records supporting three expense types
- Fields:
  - `payee`: Foreign key to Payee (PROTECT delete - cannot delete payee if linked)
  - `title`: Expense description (CharField, max 255)
  - `expense_type`: Type choice (endless_recurring, split_payment, one_time)
  - `total_amount`: Total expense amount (DecimalField, 13,2, min 0.01)
  - `installments_count`: Number of installments (PositiveIntegerField, default 0)
  - `started_at`: When expense begins (DateField)
  - `closed_at`: When expense completed (DateTimeField, optional)
  - `created_at`: Automatic timestamp (DateTimeField)
  - `updated_at`: Automatic timestamp (DateTimeField)
- Business Rules:
  - Split payments must have installments_count > 0
  - Other types must have installments_count = 0
  - **started_at cannot be earlier than current month (prevents historical data creation)**
  - **Default start date in forms is first day of current month**
  - closed_at cannot be in the future
  - Ordered by creation date descending
  - Payment method is now property of individual payments (ExpenseItems)

#### ExpenseItem Model

- Purpose: Individual payment instances linked to expenses and months
- Fields:
  - `expense`: Foreign key to Expense (CASCADE delete)
  - `month`: Foreign key to Month (CASCADE delete)
  - `payment_method`: Foreign key to PaymentMethod (SET_NULL delete, optional)
  - `due_date`: When payment is due (DateField)
  - `payment_date`: When payment was made (DateField, optional)
  - `amount`: Payment amount (DecimalField, 13,2, min 0.01)
  - `status`: Payment status (pending, paid)
  - `created_at`: Automatic timestamp (DateTimeField)
  - `updated_at`: Automatic timestamp (DateTimeField)
- Business Rules:
  - Paid items must have payment_date
  - Pending items cannot have payment_date
  - Status and payment_date must be consistent
  - Payment method can be different for each payment (supports chunked payments)
  - Ordered by due_date, then creation date

### 2.2 Relationships

#### Primary Relationships:

- Expense → Payee (Many-to-One, required)
- ExpenseItem → Expense (Many-to-One, required)
- ExpenseItem → Month (Many-to-One, required)
- ExpenseItem → PaymentMethod (Many-to-One, optional)

#### Delete Behavior:

- Payee deletion → PROTECTED (prevents deletion if linked to any expenses)
- PaymentMethod deletion → Set NULL on ExpenseItems
- Expense deletion → Cascade to ExpenseItems
- Month deletion → Cascade to ExpenseItems (only allowed for most recent month with no paid items)

### 2.3 Data Validation

#### Model-Level Validation:

- Expense type consistency with installments count
- **Start date validation (cannot be earlier than current month)**
- Date field validation (no future dates where inappropriate)
- Amount validation (positive values only)
- Status consistency with payment dates

#### Database Constraints:

- Unique constraints on Payee/PaymentMethod names
- Unique constraint on Month year/month combination
- Check constraints for valid date ranges
- **Application-level validation for start date restrictions**
- Foreign key constraints with proper cascading

## 3. Admin Interface Requirements

### 3.1 Administrative Features

#### Common Features for All Models:

- List views with relevant fields displayed
- Search functionality where appropriate
- Filtering options for key fields
- Readonly fields for timestamps
- Optimized queries to prevent N+1 problems

#### Payee Admin:

- Display: name, created_at
- Search: name
- Features: Basic CRUD operations

#### PaymentMethod Admin:

- Display: name, created_at
- Search: name
- Features: Basic CRUD operations

#### Month Admin:

- Display: year, month, created_at, (indicator if has paid expenses)
- Filter: year, month
- Features: View existing months, create sequential months only, delete most recent unpaid month only
- Validation: Enforce sequential creation and deletion rules

#### Expense Admin:

- Display: title, payee, expense_type, total_amount, started_at, closed_at
- Filter: expense_type, closed_at, payee
- Search: title, payee name
- Features: Full CRUD with date hierarchy, #### start date validation**
- **Form defaults: start date set to current month's first day**
- Performance: Select related payee/payment_method

#### ExpenseItem Admin:

- Display: expense, month, due_date, amount, status, payment_date, payment_method
- Filter: status, month, expense type, payment_method
- Search: expense title, payee name
- Features: Payment management interface with payment method selection
- Performance: Select related expense/payee/month/payment_method

### 3.2 User Experience

#### Admin Interface Goals:

- Quick data entry for testing and initial setup
- Clear visualization of expense relationships
- Easy navigation between related objects
- Efficient bulk operations where needed

## 4. Data Setup Requirements

### 4.1 Initial Data

#### Reference Data (Fixtures):

- 5 sample payees (Electric Company, Internet Provider, etc.)
- 5 payment methods (Credit Card, Debit Card, Bank Transfer, Cash, PayPal)
- Initial seed month (current year/month or specified in settings)
- Proper timestamps for all fixture data

#### Management Commands:

- `setup_initial_data`: Load reference data fixtures and create initial month
- Error handling and user feedback
- Idempotent operation (safe to run multiple times)
- Ensures system has required seed month for operation

### 4.2 Database Initialization

#### Migration Strategy:

- Single initial migration with all models
- Proper field definitions and constraints
- Index creation for performance
- Foreign key relationships established

#### Setup Process:

1. Run Django migrations
2. Create superuser for admin access
3. Load initial data fixtures
4. Verify model functionality

## 5. Technical Implementation

### 5.1 Django Best Practices

#### Model Implementation:

- Proper `__str__` methods for admin display
- Meta classes with ordering and unique constraints
- Clean methods for custom validation
- Appropriate field types and validators

#### Performance Considerations:

- Database indexes on frequently queried fields
- Select_related in admin querysets
- Appropriate max_length values
- Efficient ordering specifications

### 5.2 Quality Assurance

#### Validation Testing:

- Model clean methods work correctly
- Database constraints prevent invalid data
- Admin interface handles edge cases
- Fixtures load without errors

#### Integration Testing:

- All model relationships function properly
- Admin interface creates/updates data correctly
- Management commands execute successfully
- Database operations perform efficiently

## 6. Future Phase Integration

### 6.1 Readiness for Phase 2

#### Business Logic Foundation:

- Models support all three expense types
- Monthly processing structure in place
- Payment tracking mechanisms ready
- Completion workflow supported

#### Interface Preparation:

- Admin interface validates business rules
- Model methods ready for view layer
- Query optimization established
- Data integrity guaranteed

### 6.2 Extension Points

#### Planned Enhancements:

- Additional model methods for business logic
- Custom managers for common queries
- Signal handlers for automatic processing
- Advanced validation rules

## 7. Acceptance Criteria

### 7.1 Functional Requirements

#### ✅ Model Creation:

- All 5 models implemented with correct fields
- Relationships properly defined
- Validation rules enforced

#### ✅ Database Operations:

- Migrations create proper schema
- CRUD operations work for all models
- Constraints prevent invalid data

#### ✅ Admin Interface:

- All models registered and functional
- Search and filtering work correctly
- Performance optimization implemented

#### ✅ Data Management:

- Initial data loads successfully
- Management commands work properly
- Test data can be created/modified

### 7.2 Technical Requirements

#### ✅ Code Quality:

- Models follow Django conventions
- Proper documentation and comments
- Consistent naming and structure

#### ✅ Performance:

- Database queries optimized
- Admin interface responsive
- Appropriate indexing in place

#### ✅ Validation:

- Model validation prevents invalid data
- Business rules enforced at database level
- Error messages clear and helpful

This Phase 1 implementation provides a solid foundation for the expense tracking system, with all
core data structures properly defined and validated. The models support the full range of expense
types and workflows defined in the main PRD, setting the stage for successful Phase 2 development of
business logic and user interfaces.
