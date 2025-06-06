# Restrict Expense Item Date Editing PRD

**Ticket**: [Restrict expense item date editing to not exceed the month it was created in](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/86)

## Problem Statement

Users can currently edit expense item dates without restrictions, potentially moving expense items
to different months than where the parent expense was originally created. This creates data
integrity issues and breaks the logical connection between expenses and their designated monthly
tracking periods, making monthly expense reporting inconsistent and unreliable.

## Solution Overview

Implement validation that restricts expense item date editing to remain within the month boundaries
of the original expense creation. When users attempt to edit an expense item's due date, the system
will validate that the new date falls within the same month (year-month) as when the expense was
originally created. This maintains data integrity while still allowing reasonable date adjustments
within the correct monthly period.

## User Stories

1. As a user editing an expense item, I want the system to prevent me from changing the date to a
   different month, so that my monthly expense tracking remains accurate
1. As a user, I want to still be able to adjust expense item dates within the same month, so that I
   can correct due dates while maintaining proper categorization
1As a user, I want clear error messages when my date changes are invalid, so that I understand why
   my edit was rejected and what dates are acceptable

## Acceptance Criteria

- [ ] Expense item date editing is restricted to the same month (year-month) as the original expense creation month
- [ ] Users can still modify dates within the allowed month range (e.g., January 5 to January 28)
- [ ] System displays clear validation error when user attempts to set date outside allowed month
- [ ] Validation occurs both client-side and server-side for security
- [ ] Existing expense items retain their current dates without modification
- [ ] Date validation respects the expense's original creation month, not the current system month

## Out of Scope

- Editing expense item amounts or other non-date fields
- Changing the core expense date validation logic
- Moving entire expenses between months
- Bulk editing of multiple expense items
- Complex date range validations beyond month boundaries
- UI redesign for expense item editing forms

## Success Metrics

1. Zero expense items exist with dates outside their parent expense's creation month after implementation
2. User attempts to edit dates outside month boundaries are blocked 100% of the time
3. Valid date edits within month boundaries complete successfully without errors
