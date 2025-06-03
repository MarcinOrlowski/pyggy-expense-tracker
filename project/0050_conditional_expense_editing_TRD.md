# Conditional Expense Editing TRD

**Last Updated**: January 6, 2025
**Ticket**: [#50](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/50)
**PRD Reference**: 0050_conditional_expense_editing_PRD.md

## Technical Approach
We'll extend the existing expense editing functionality by adding validation methods to the Expense model that determine edit permissions based on payment status and expense type. The expense_edit view will check these permissions before rendering the form, and the ExpenseForm will dynamically disable fields based on edit restrictions. We'll use Django's messaging framework to communicate restrictions to users and update the UI to conditionally show/hide the edit button with appropriate tooltips.

## Data Model
No database changes required. We'll add methods to the existing Expense model:
```python
# Expense model additions
- can_be_edited() -> bool  # Overall edit permission
- can_edit_amount() -> bool  # Amount field edit permission
- get_edit_restrictions() -> dict  # Detailed restrictions and reasons
```

## API Design
No new endpoints. Modifications to existing views:
```
GET /budgets/<budget_id>/expenses/<pk>/edit/
- Check can_be_edited() before rendering
- Return 403 with message if editing not allowed
- Pass edit restrictions to template context

POST /budgets/<budget_id>/expenses/<pk>/edit/
- Validate edit permissions before processing
- Check field-level permissions for amount changes
- Return form errors if validation fails
```

## Security & Performance
- Authorization: Existing budget-based access control maintained
- Validation: Server-side enforcement of edit restrictions
- Performance: < 10ms overhead for permission checks (in-memory calculations)
- No caching needed as permissions are derived from existing data

## Technical Risks & Mitigations
1. **Risk**: Users bypassing UI restrictions via direct POST → **Mitigation**: Server-side validation in form.clean()
2. **Risk**: Race condition between payment and edit → **Mitigation**: Atomic transaction with select_for_update()
3. **Risk**: Confusion about partial edit permissions → **Mitigation**: Clear field-level messaging and disabled state

## Implementation Plan
- Phase 1 (S): Add permission methods to Expense model - 1 hour
- Phase 2 (M): Update expense_edit view and form validation - 2 hours
- Phase 3 (S): Modify UI to show/hide edit button conditionally - 1 hour
- Phase 4 (S): Add form field disabling and user messaging - 1 hour
- Phase 5 (S): Testing and edge case handling - 1 hour

Dependencies: None

## Monitoring & Rollback
- Feature flag: None (extending existing functionality)
- Key metrics: Edit attempt failures, 403 responses on edit endpoint
- Rollback: Revert commit; no data migration needed