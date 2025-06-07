# Multiple Payments per Expense PRD

**Ticket**: [Rework payments to allow multiple payments per expense](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/100)

## Problem Statement

Users cannot record partial payments for expenses, forcing them to either wait until they can pay the full amount or lose track of partial payments made. This creates inaccurate payment tracking and prevents users from properly managing cash flow and payment schedules. The current binary paid/unpaid system doesn't reflect real-world payment scenarios where users often make multiple payments toward a single expense.

## Solution Overview

Enable users to record multiple partial payments against a single expense item until the total payments equal the due amount. The system will track individual payment records, prevent overpayments by capping payment amounts at the remaining balance, and automatically mark expenses as fully paid when total payments reach the due amount. Users can continue using the existing payment workflow with enhanced capability to make partial payments.

## User Stories

1. As a user, I want to record a partial payment on an expense, so that I can track progress toward paying off larger bills
2. As a user, I want to see how much I still owe on an expense, so that I know exactly how much more I need to pay  
3. As a user, I want the system to prevent me from overpaying, so that I don't accidentally pay more than what's due
4. As a user, I want to see all payments I've made on an expense, so that I have a complete payment history
5. As a user, I want expenses to automatically be marked as paid when I've paid the full amount, so that my payment status is always accurate

## Acceptance Criteria

- [ ] User can record multiple payments against a single expense item
- [ ] System prevents payment amounts that exceed the remaining balance
- [ ] Expense items show total paid amount and remaining balance  
- [ ] Expense items are automatically marked as "paid" when total payments >= due amount
- [ ] Payment history is visible for each expense item
- [ ] Existing expense completion logic works with new payment system
- [ ] Migration preserves all existing payment data

## Out of Scope

- Payment editing or deletion functionality
- Payment management dashboard or admin interface
- Payment analytics or reporting features
- Support for negative payments or refunds
- Payment method changes after payment is recorded
- Batch payment operations

## Success Metrics

1. Users can successfully record partial payments without system errors
2. Zero cases of overpayment due to system validation
3. All existing expense completion workflows continue to function correctly