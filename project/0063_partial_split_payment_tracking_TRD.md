# Partial Split Payment Tracking TRD

**Ticket**: [Allow partial split payment tracking with configurable start installment](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/63)
**PRD Reference**: 0063_partial_split_payment_tracking_PRD.md

## Technical Approach

We'll add an `initial_installment` field to the existing Expense model as a non-nullable integer
with default 0. The Django form will conditionally show this field only for split payment types and
make it read-only during edits. The expense item generation logic in `services.py` will be updated
to account for the starting installment offset when calculating completion and display numbering.

## Data Model

```sql
-- Migration: Add initial_installment field to expenses_expense table
ALTER TABLE expenses_expense 
ADD COLUMN initial_installment INTEGER DEFAULT 0 NOT NULL;

-- Update model validation and clean() method
-- Field constraints:
-- - Only used when expense_type = 'split_payment' 
-- - Must be >= 0 and < installments_count
-- - Immutable after expense creation
```

Updated Expense model documentation:

```python
SPLIT_PAYMENT ('split_payment'):
    - total_amount: Monthly installment amount (not total cost)
    - started_at: Start date for first installment
    - installments_count: Total number of installments (must be > 0)
    - initial_installment: Starting installment number (0-based, default 0)
    - end_date: Not used (must be None)
    - Notes: Creates (installments_count - initial_installment) expense items
```

## Form & UI Changes

**ExpenseForm Updates:**

```python
# Add field to Meta.fields
fields = [..., 'initial_installment']

# Conditional visibility via JavaScript
# Show only when expense_type == 'split_payment'
# Make read-only when editing existing expense

# Validation in clean()
if expense_type == TYPE_SPLIT_PAYMENT:
    if initial_installment < 0 or initial_installment >= installments_count:
        raise ValidationError('Initial installment must be between 0 and installments_count - 1')
```

**Template Updates:**

- Add field with conditional display logic
- Update installment display to show "Installment X of Y" format
- X = current_installment_number + initial_installment + 1

## Service Logic Changes

**create_expense_items_for_month() Updates:**

```python
elif expense.expense_type == expense.TYPE_SPLIT_PAYMENT:
    existing_count = ExpenseItem.objects.filter(expense=expense).count()
    remaining_installments = expense.installments_count - expense.initial_installment
    
    if existing_count < remaining_installments:
        # Create expense item with adjusted numbering
```

**check_expense_completion() Updates:**

```python
elif expense.expense_type == expense.TYPE_SPLIT_PAYMENT:
    paid_items = ExpenseItem.objects.filter(expense=expense, status='paid').count()
    remaining_installments = expense.installments_count - expense.initial_installment
    
    if paid_items >= remaining_installments:
        # Mark as completed
```

## Security & Performance

- **Data Integrity**: Field validation prevents invalid initial_installment values
- **Immutability**: Form-level and model-level enforcement prevents modification after creation
- **Migration Safety**: Non-nullable field with default value ensures safe deployment
- **Performance Impact**: Minimal - single integer field addition with no additional queries

## Technical Risks & Mitigations

1. **Risk**: Existing split payment expenses break due to new field → **Mitigation**: Default value 0 maintains backward compatibility
2. **Risk**: Complex UI logic for conditional field display → **Mitigation**: Reuse existing expense type switching JavaScript patterns
3. **Risk**: Migration conflicts on production data → **Mitigation**: Non-destructive migration with default value

## Implementation Plan

- Phase 1 (S): Database migration + model updates - 1 hour
- Phase 2 (M): Form field addition + validation logic - 2 hours  
- Phase 3 (M): Service logic updates for item generation/completion - 2 hours
- Phase 4 (S): Template updates for display formatting - 1 hour
- Phase 5 (S): Test updates and edge case validation - 1 hour

Dependencies: None

## Monitoring & Rollback

- **Migration Rollback**: Standard Django migration reverse (removes column)
- **Feature Validation**: Verify new split payments calculate remaining installments correctly
- **Edge Cases**: Test with various initial_installment values (0, middle, max-1)
- **Backward Compatibility**: Ensure existing split payments (initial_installment=0) work unchanged
