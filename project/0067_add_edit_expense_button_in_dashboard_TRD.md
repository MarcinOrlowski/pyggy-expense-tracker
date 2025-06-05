# Add Edit Expense Button in Dashboard TRD

**Last Updated**: 2025-01-06
**Ticket**: [#0067](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/67)
**PRD Reference**: 0067_add_edit_expense_button_in_dashboard_PRD.md

## Technical Approach

We'll modify the existing `expense_items_table.html` template to add a conditional edit button in
the actions column. The button will only render when `item.expense.can_be_edited()` returns True,
leveraging the existing conditional editing logic from #0050. The button will use Font Awesome icons
consistent with other action buttons and link to the existing expense edit view.

## Data Model

No data model changes required - using existing `Expense.can_be_edited()` method.

## API Design

No API changes - using existing URL pattern: `{% url 'expense_edit' budget.id item.expense.pk %}`

## Security & Performance

- Authorization: Existing expense edit view handles permissions
- Performance: Minimal impact - one additional method call per expense item
- No caching needed as `can_be_edited()` checks are lightweight

## Technical Risks & Mitigations

1. **Risk**: Template complexity with multiple conditional buttons → **Mitigation**: Keep button
   rendering logic simple and consistent with existing patterns
1. **Risk**: User confusion about why some expenses have edit buttons and others don't → *
   *Mitigation**: Clear tooltip text and consistent visual hierarchy

## Implementation Plan

- Update template (S): Modify `expense_items_table.html` to add conditional edit button - 30 min
- Testing (S): Verify button appears/disappears correctly for different expense types - 15 min

Dependencies: None - all required functionality already exists

## Monitoring & Rollback

- Feature flag: Not needed for template-only change
- Key metrics: None - UI-only change
- Rollback: Revert template change if issues arise
