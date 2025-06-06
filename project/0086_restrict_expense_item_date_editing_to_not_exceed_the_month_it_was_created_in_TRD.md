# Restrict Expense Item Date Editing TRD

**Ticket**: [Restrict expense item date editing to not exceed the month it was created in](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/86)
**PRD Reference**: 0086_restrict_expense_item_date_editing_to_not_exceed_the_month_it_was_created_in_PRD.md

## Technical Approach

We'll implement expense item date validation by adding a new method to the ExpenseItem model that
validates the due_date against the parent expense's creation month. A new ExpenseItemEditForm will
handle the editing UI with both client-side JavaScript validation and server-side Django form
validation. The implementation will reuse existing Django patterns for form validation and error
handling, adding a new view for expense item editing that integrates with the current expense detail
page.

## Data Model

No database schema changes required. We'll add new model methods to existing models:

```python
# expenses/models.py - ExpenseItem class additions
def get_allowed_month_range(self):
    """Returns (start_date, end_date) tuple for allowed month range"""
    expense_month = self.expense.started_at
    year, month = expense_month.year, expense_month.month
    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year, month)[1])
    return (start_date, end_date)

def clean(self):
    """Add validation for due_date within expense creation month"""
    if self.due_date and self.expense_id:
        start_date, end_date = self.get_allowed_month_range()
        if not (start_date <= self.due_date <= end_date):
            raise ValidationError(f'Due date must be within {start_date.strftime("%B %Y")}')
```

## API Design

No new API endpoints required. We'll add new views following existing Django patterns:

```python
# expenses/views.py additions
def expense_item_edit(request, budget_id, pk):
    """Edit expense item due date with month validation"""
    # GET: Render form with current values
    # POST: Validate and save changes

# expenses/urls.py addition
path('budgets/<int:budget_id>/expense-items/<int:pk>/edit/', 
     views.expense_item_edit, name='expense_item_edit')
```

Form handling follows existing pattern with validation errors displayed via Django messages framework.

## Security & Performance

- Authentication: Existing budget-based permission checking (expense item must belong to accessible budget)
- Input validation: Django form validation with additional custom due_date validation
- Performance: No additional database queries (expense relationship already loaded)
- CSRF protection: Standard Django CSRF tokens on all forms

## Technical Risks & Mitigations

1. **Risk**: Users with existing invalid expense items may be locked out → **Mitigation**:
   Validation only applies to edits, not existing data
1. **Risk**: Complex month boundary edge cases (leap years, timezone issues) → **Mitigation**: Use
   Python's calendar module and date objects for reliable month calculations
1. **Risk**: Form submission bypassing client-side validation → **Mitigation**: Server-side
   validation is primary, client-side is UX enhancement only

## Implementation Plan

- Phase 1 (S): Add ExpenseItem model validation methods - 1 hour
- Phase 2 (M): Create ExpenseItemEditForm and validation logic - 2 hours  
- Phase 3 (M): Add expense_item_edit view and URL routing - 2 hours
- Phase 4 (S): Update expense detail template with edit links - 1 hour
- Phase 5 (M): Add comprehensive test coverage - 2 hours
- Phase 6 (S): Client-side JavaScript validation enhancement - 1 hour

Dependencies: None (uses existing Django patterns and models)

## Monitoring & Rollback

- Feature flag: Not required (simple form validation addition)
- Key metrics: Monitor for form validation errors in logs to track usage patterns
- Rollback: Remove edit links from templates and validation from models if issues arise
- Logging: Django form validation errors automatically logged for debugging
