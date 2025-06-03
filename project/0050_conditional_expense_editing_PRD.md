# Conditional Expense Editing PRD

**Last Updated**: January 6, 2025
**Ticket**: [#50](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/50)

## Problem Statement
Users cannot modify expenses after adding them to a month, even when the expense hasn't been paid yet. This forces users to delete and recreate expenses to fix typos or adjust amounts, losing any associated history. This impacts data accuracy and creates frustration for users managing their budgets.

## Solution Overview
Add conditional editing capabilities to existing expenses based on their payment and recurrence status. Users can edit unpaid non-recurring expenses freely, edit names/notes on any expense, and modify amounts only on unpaid expenses. The system will provide clear visual indicators and informative messages explaining why certain edits are restricted.

## User Stories
1. As a user, I want to edit unpaid expenses after adding them to a month, so that I can correct mistakes without losing expense history
2. As a user, I want to update expense names and notes even after payment, so that I can maintain accurate records
3. As a user, I want to understand why I cannot edit certain expenses, so that I know the system is protecting my payment history

## Acceptance Criteria
- [ ] Users can edit all fields of unpaid, non-recurring expenses
- [ ] Users can edit name and notes fields of any expense regardless of payment status
- [ ] Users cannot edit amounts of paid expenses
- [ ] Users cannot edit recurring expenses (split payment or recurring with end date)
- [ ] Users can edit amounts of endless recurring expenses only if unpaid
- [ ] System displays clear messages explaining why editing is restricted
- [ ] Edit button is hidden/disabled with tooltip when editing is not allowed

## Out of Scope
- Bulk editing of multiple expenses
- Editing expense items individually
- Changing expense type after creation
- Editing closed expenses
- Version history or audit trail of edits

## Success Metrics
1. 80% reduction in expense deletion/recreation within first month
2. Zero data integrity issues from expense editing
3. User support tickets about expense editing drop by 50%