# Partial Split Payment Tracking PRD

**Ticket**: [Allow partial split payment tracking with configurable start installment](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/63)

## Problem Statement

Users cannot track split payment expenses when they start using the system mid-way through an
installment plan. Currently, split payments always begin from installment #1, forcing users to
either create inaccurate records or manually track partial payment histories outside the system.
This affects 100% of users who have existing payment plans when adopting the expense tracker.

## Solution Overview

Add an `initial_installment` field to split payment expenses that allows users to specify which
installment number they want to start tracking from (default 0 for installment #1). The system will
correctly calculate remaining payments and display accurate installment numbering like "Installment
5 of 10" for partial tracking scenarios. This field becomes immutable after expense creation to
maintain data integrity.

## User Stories

1. As a user with existing payment plans, I want to specify which installment I'm starting to track
   from, so that my records accurately reflect my real payment progress
1. As a user viewing expense details, I want to see clear installment numbering (e.g., "Installment
   5 of 10"), so that I understand my payment position in the plan
1As a user managing expenses, I want the system to automatically calculate remaining payments
   based on my starting point, so that completion tracking works correctly

## Acceptance Criteria

- [ ] Users can specify starting installment number (0-based) when creating split payment expenses
- [ ] Initial installment field defaults to 0 (meaning start from installment #1)
- [ ] Initial installment field is only visible and editable for split payment expense type
- [ ] Initial installment field becomes read-only after expense creation
- [ ] System displays installment progress as "Installment X of Y" where X reflects the actual installment number
- [ ] Expense completion logic correctly accounts for partial tracking (closes when all remaining installments are paid)
- [ ] Form validation ensures initial installment is between 0 and installments_count - 1

## Out of Scope

- Modifying initial installment after expense creation
- Retrospective payment history for skipped installments
- Different installment amounts for partial tracking
- Bulk editing of existing split payment expenses
- Integration with external payment tracking systems

## Success Metrics

1. Users can successfully create partial split payment expenses without workarounds
2. Installment numbering displays correctly for both full and partial tracking scenarios
3. Expense completion detection works accurately for partial payment plans
