# Restrict Expense Date Editing to Future Dates Only PRD

**Ticket**: [#0084](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/84)

## Problem Statement

Users can currently modify expense dates to historical dates when editing expenses, which
compromises data integrity and financial tracking accuracy. This creates confusion when reconciling
past financial records and undermines the purpose of maintaining a chronological expense history.
Without proper date editing restrictions, users may inadvertently corrupt their financial timeline.

## Solution Overview

Implement date validation rules that restrict expense date editing based on the expense's current
date and the system's active month. Users can only edit expense dates if the current date is not
earlier than next month, and when editing is allowed, the new date must be in the future or no
earlier than the currently active month plus one. This ensures financial data integrity while
providing flexibility for legitimate date corrections.

## User Stories

1. As a user editing an expense, I want to be prevented from setting historical dates, so that my
   financial records maintain chronological integrity
1. As a user with an expense from the current active month, I want to be able to update the date to
   future months only, so that I can correct upcoming payment schedules without corrupting past data
1As a user trying to edit an old expense date, I want to see clear error messages explaining why
   the edit is restricted, so that I understand the system's validation rules

## Acceptance Criteria

- [ ] Users cannot edit expense dates if the current expense date is earlier than next month (current month + 1)
- [ ] When date editing is allowed, users can only set dates to future dates or no earlier than active month + 1
- [ ] Clear validation error messages display when users attempt invalid date changes
- [ ] The UI clearly indicates when date editing is restricted (disabled field or visual indicator)
- [ ] Existing date validation logic remains intact and continues to work
- [ ] Form submission is blocked when invalid date changes are attempted

## Out of Scope

- Bulk date editing for multiple expenses
- Admin override capabilities for date restrictions
- Historical date editing for specific user roles
- Import/migration tools for historical data correction
- Expense date range editing (start and end dates as a group)

## Success Metrics

1. Zero invalid historical date updates are saved to the database
2. Users receive clear feedback on date editing restrictions within 1 second of input
3. Existing expense editing functionality remains unaffected for valid date changes
