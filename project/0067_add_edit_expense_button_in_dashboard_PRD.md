# Add Edit Expense Button in Dashboard PRD

**Last Updated**: 2025-01-06
**Ticket**: [#0067](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/67)

## Problem Statement
The dashboard currently shows expenses but users cannot directly edit them from this view. They must navigate to the expense detail page first, which adds unnecessary clicks to the workflow for quick edits.

## Solution Overview
Add an edit button with pencil icon next to each expense in the dashboard expense items table. The button will only appear when the expense is editable according to the conditional editing rules implemented in #0050. This provides direct access to the expense edit form from the dashboard, improving user workflow efficiency.

## User Stories
1. As a user, I want to edit expenses directly from the dashboard, so that I can make quick changes without extra navigation
2. As a user, I want to see edit buttons only for editable expenses, so that I understand which expenses can be modified
3. As a user, I want consistent action buttons across the interface, so that I can quickly identify available actions

## Acceptance Criteria
- [ ] Edit button with pencil icon (`fa-pencil`) appears next to each expense in dashboard expense items table
- [ ] Edit button only displays when `expense.can_be_edited()` returns True
- [ ] Edit button links to the expense edit form (`expense_edit` URL) with correct parameters
- [ ] Edit button has tooltip text "Edit Expense" for accessibility
- [ ] Edit button follows existing styling (`btn btn-sm`) and positioning patterns
- [ ] Edit button appears in the actions column alongside existing buttons

## Out of Scope
- Modifying the conditional editing logic itself
- Adding edit buttons to other views outside the dashboard
- Inline editing within the table
- Changing the existing button layout or styling patterns

## Success Metrics
1. Users can access expense edit form with one click from dashboard
2. No edit buttons appear for non-editable expenses (split payments, recurring with end date, closed expenses)
3. Edit action maintains consistency with existing UI patterns