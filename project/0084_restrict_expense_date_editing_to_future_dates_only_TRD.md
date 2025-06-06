# Restrict Expense Date Editing to Future Dates Only TRD

**Ticket**: [#0084](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/84)
**PRD Reference**: 0084_restrict_expense_date_editing_to_future_dates_only_PRD.md

## Technical Approach

We'll extend the existing expense editing validation system by adding new date editing restriction
methods to the `Expense` model and updating the `ExpenseForm` validation logic. The implementation
will leverage the existing `Month.get_most_recent()` method to determine the current active month
and add `can_edit_date()` method to the expense model alongside existing editing restrictions. Form
validation will occur in both `ExpenseForm.clean()` and the model's `clean()` method to ensure data
integrity.

## Data Model

No database schema changes required. The implementation extends existing model methods:

```python
# New methods added to Expense model
def can_edit_date(self):
    """Check if the start date can be edited based on current date restrictions"""
    
def get_next_month_date(self):
    """Calculate next month start date for this expense's budget"""

# Updated method in ExpenseForm  
def clean_started_at(self):
    """Enhanced validation for date editing restrictions"""
```

## API Design

No new API endpoints required. Updates to existing expense edit functionality:

```python
# Form validation enhancement
POST /expenses/{budget_id}/{expense_id}/edit/
Request: { started_at: "2024-02-15", ... }
Validation: Check date editing restrictions before allowing change
Response: ValidationError if date editing not allowed

# Frontend form behavior
- Disable date field if editing not allowed
- Show error message for invalid date attempts
- Preserve existing form validation flow
```

## Security & Performance

- **Validation**: Double validation in both form and model `clean()` methods to prevent bypass attempts
- **Performance**: <5ms additional validation time using existing database queries and date calculations
- **Authorization**: Leverages existing expense ownership validation through budget_id parameter
- **Data integrity**: Prevents historical date corruption through server-side validation

## Technical Risks & Mitigations

1. **Risk**: Users bypass frontend validation via direct form submission → **Mitigation**: Server-side validation in model `clean()` method ensures data integrity
2. **Risk**: Complex date calculation logic introduces bugs → **Mitigation**: Use existing `Month.get_most_recent()` pattern and comprehensive unit tests
3. **Risk**: Breaking existing expense editing functionality → **Mitigation**: Incremental validation additions that preserve existing behavior for valid cases

## Implementation Plan

- Phase 1 (S): Add `can_edit_date()` method to Expense model with unit tests - 1 day
- Phase 2 (M): Update ExpenseForm validation logic and error messages - 1 day  
- Phase 3 (S): Update form templates to disable date field when restricted - 0.5 day
- Phase 4 (S): Integration testing and CHANGES.md entry - 0.5 day

Dependencies: None - builds on existing expense editing infrastructure

## Monitoring & Rollback

- **Feature flag**: Not needed - validation enhancement with graceful degradation
- **Key metrics**: Monitor expense edit form submission errors and success rates
- **Rollback**: Remove new validation methods and revert to original form validation if critical issues arise
- **Testing**: Verify existing expense editing functionality remains intact for all valid scenarios
