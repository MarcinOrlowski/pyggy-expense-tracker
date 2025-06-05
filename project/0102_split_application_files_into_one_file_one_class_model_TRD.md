# Split Application Files into One-File-One-Class Model TRD

**Ticket**: [Split application files into one-file-one-class model for better granularity](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/102)
**PRD Reference**: Split Application Files into One-File-One-Class Model PRD

## Technical Approach

We'll implement a three-phase incremental refactoring approach starting with models (foundation),
then views (business logic), then forms (UI layer). Each phase will create new directory structures,
move code into logical modules, update all import statements, and maintain Django framework
compatibility through minimal `__init__.py` files. All existing functionality remains unchanged -
this is purely a file organization refactoring.

## File Structure Changes

### Phase 1: Models Refactoring

```text
expenses/models/
├── __init__.py          # Django model discovery: from .budget import Budget, etc.
├── budget.py           # Budget class (44 lines)
├── payee.py            # Payee class (18 lines)
├── payment_method.py   # PaymentMethod class (13 lines)
├── month.py            # Month class (44 lines)
├── expense.py          # Expense class (297 lines)
├── expense_item.py     # ExpenseItem class (87 lines)
└── settings.py         # Settings class (38 lines)
```

### Phase 2: Views Refactoring

```text
expenses/views/
├── __init__.py          # Empty
├── dashboard.py         # dashboard view (~100 lines)
├── expense.py          # expense_list, expense_create, expense_detail, expense_edit, expense_delete (~160 lines)
├── month.py            # month_list, month_detail, month_delete, month_process (~130 lines)
├── payment.py          # expense_item_pay, expense_item_unpay, expense_item_edit (~90 lines)
├── payee.py            # payee_list, payee_create, payee_edit, payee_delete, payee_hide, payee_unhide (~110 lines)
├── payment_method.py   # payment_method_list, payment_method_create, payment_method_edit, payment_method_delete (~70 lines)
└── budget.py           # budget_list, budget_create, budget_edit, budget_delete (~80 lines)
```

### Phase 3: Forms Refactoring

```text
expenses/forms/
├── __init__.py          # Empty
├── expense.py          # ExpenseForm (~145 lines)
├── payment.py          # PaymentForm, ExpenseItemEditForm (~61 lines)
├── payee.py            # PayeeForm (~9 lines)
├── budget.py           # BudgetForm (~45 lines)
└── payment_method.py   # PaymentMethodForm (~8 lines)
```

## Import Statement Updates

### Phase 1 Model Import Changes

```python
# Before
from .models import Budget, Expense, ExpenseItem, Month, Payee, PaymentMethod

# After  
from .models.budget import Budget
from .models.expense import Expense
from .models.expense_item import ExpenseItem
from .models.month import Month
from .models.payee import Payee
from .models.payment_method import PaymentMethod
```

### Phase 2 URL Pattern Changes

```python
# Before
from . import views
path('budgets/<int:budget_id>/dashboard/', views.dashboard, name='dashboard')

# After
from .views import dashboard, expense, month, payment, payee, payment_method, budget
path('budgets/<int:budget_id>/dashboard/', dashboard.dashboard, name='dashboard')
```

### Phase 3 View Import Changes

```python
# Before
from .forms import ExpenseForm, PaymentForm, PayeeForm

# After
from .forms.expense import ExpenseForm
from .forms.payment import PaymentForm
from .forms.payee import PayeeForm
```

## Security & Performance

- No security implications: Pure file organization refactoring
- No performance impact: Python import caching handles module structure efficiently
- Django framework compatibility: `models/__init__.py` maintains model discovery
- Migration safety: Django migrations reference string paths resolved via `__init__.py`

## Technical Risks & Mitigations

1. **Risk**: Circular import issues between models → **Mitigation**: Careful import ordering, use
   string references for ForeignKeys if needed
2. **Risk**: Django migration path resolution breaks → **Mitigation**: `models/__init__.py`
   maintains all model imports for framework compatibility
3. **Risk**: Test import failures → **Mitigation**: Update all test imports in single atomic commit
   per phase

## Implementation Plan

- Phase 1 (L): Models refactoring + import updates - 4 hours
  - Create `models/` directory structure
  - Split model classes into individual files
  - Create `models/__init__.py` with Django-required imports
  - Update all imports in views, forms, admin, services, tests
  - Run full test suite
- Phase 2 (L): Views refactoring + URL updates - 3 hours
  - Create `views/` directory structure
  - Group view functions by functional area
  - Update `urls.py` import statements
  - Run full test suite
- Phase 3 (M): Forms refactoring + view updates - 2 hours
  - Create `forms/` directory structure
  - Group form classes by related functionality
  - Update view imports
  - Run full test suite

Dependencies: None - self-contained refactoring

## Monitoring & Rollback

- Feature flag: Not applicable (file organization change)
- Key metrics: Test suite pass rate (must remain 100%)
- Rollback: Git revert individual phase commits if issues arise
- Validation: `./manage.py test` after each phase completion
