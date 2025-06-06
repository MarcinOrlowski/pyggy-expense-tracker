# Recurring with End Date Expense Type TRD v1.0

**Last Updated**: January 6, 2025  
**Author**: Claude  
**PRD Reference**: v1.0  
**Status**: Approved

## Technical Approach

We'll extend the existing expense system by adding a new expense type `recurring_with_end` and an
optional `end_date` field to the Expense model. The expense item generation logic in `services.py`
will be updated to handle this new type, checking if the current month is beyond the end date month
before creating items. The form will conditionally show the end date field and calculate the total
number of payments for user preview.

## Data Model

```python
# Expense model changes
class Expense:
    EXPENSE_TYPES = [
        ('endless_recurring', 'Endless Recurring'),
        ('split_payment', 'Split Payment'),
        ('one_time', 'One Time'),
        ('recurring_with_end', 'Recurring with End Date'),  # NEW
    ]
    
    # New field
    end_date = models.DateField(null=True, blank=True)
    
    # Validation: end_date required only for recurring_with_end type
```

Migration will add the `end_date` field as nullable to maintain backward compatibility.

## API Design

No new API endpoints needed. Existing expense creation/update views will handle the new field:

```python
# Form validation pseudo-code
if expense_type == 'recurring_with_end':
    if not end_date:
        raise ValidationError("End date is required")
    if end_date < started_at:
        raise ValidationError("End date must be after start date")
    
# Payment count calculation for display
months_count = calculate_months_between(started_at, end_date)
```

## Security & Performance

- Validation: End date must be after or equal to start date
- Performance: No impact - same O(1) check per month processing
- Data integrity: Existing validation patterns applied to new field

## Technical Risks & Mitigations

1. **Risk**: Users might expect day-specific behavior → **Mitigation**: Clear UI labeling that payments occur through entire end month
2. **Risk**: Existing expense type changes → **Mitigation**: Make field changes conditional, preserve existing behavior
3. **Risk**: Complex month calculation logic → **Mitigation**: Use Django's date utilities and existing month processing patterns

## Implementation Plan

- **Phase 1** (S): Add model field and migration - 0.5 days
- **Phase 2** (M): Update services.py logic for new type - 1 day
- **Phase 3** (M): Update forms and templates with conditional fields - 1 day
- **Phase 4** (S): Add validation and payment preview - 0.5 days

Dependencies: None - builds on existing expense infrastructure

## Monitoring & Rollback

- Feature flag: Not needed - new expense type doesn't affect existing ones
- Key metrics: Count of new expense type usage, any validation errors
- Rollback: Remove new choice from form (existing data remains valid)

---

**Key Implementation Notes**:

1. The `create_expense_items_for_month()` function needs a new condition:

   ```python
   if expense.expense_type == 'recurring_with_end':
       if target_date > expense.end_date:
           return  # Don't create items after end date
       if target_date.year == expense.end_date.year and target_date.month == expense.end_date.month:
           # This is the last month - mark expense for closing after item creation
   ```

2. Form JavaScript to show/hide end_date field based on expense_type selection

3. Template updates to display calculated payment count before save
