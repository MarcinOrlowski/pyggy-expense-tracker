# Add Quick Payment Form to Month Dashboard PRD

**Ticket**: [Add quick payment form to month dashboard](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/149)

## Problem Statement

Users currently need to navigate away from the dashboard to the full expense creation form to add
quick one-time payments, interrupting their workflow and adding unnecessary complexity for simple
transactions. This creates friction for the most common expense type (one-time payments) and reduces
efficiency in day-to-day expense tracking. The current process requires too many steps for what
should be a simple, immediate action.

## Solution Overview

Add a streamlined quick payment form directly on the month dashboard that enables one-click creation
of one-time expenses for the current date. The form will only capture essential information (
description, payee, amount) and include an optional checkbox to automatically mark the expense as
paid with a full payment record. This eliminates navigation overhead and provides immediate access
to the most common expense creation workflow right from the primary dashboard view.

## User Stories

1. As a user, I want to quickly add a one-time expense from the dashboard, so that I can track payments without leaving my primary view
2. As a user, I want the form to default to today's date, so that I don't need to manually set the payment date for current transactions
3. As a user, I want to optionally mark expenses as immediately paid, so that I can record completed transactions in one step
4. As a user, I want access to my existing payees in a dropdown, so that I can maintain consistency in expense categorization

## Acceptance Criteria

- [ ] Quick payment form is prominently positioned on the dashboard above the expense list
- [ ] Form contains fields: expense description/title, payee (dropdown with existing payees), and amount
- [ ] Form includes checkbox labeled "Mark as paid" that auto-creates a payment record for the full amount
- [ ] Form defaults to current date and creates one-time expense type automatically
- [ ] Form submission creates expense and redirects back to dashboard with success message
- [ ] Form validation prevents empty required fields and invalid amounts
- [ ] Form only appears when user has at least one budget month created

## Out of Scope

- Custom payment dates (always uses current date)
- Multiple payment methods selection (uses default/none)
- Split payments or recurring expenses (only one-time)
- Expense editing capabilities (user edits through regular expense management)
- Payment method selection (can be edited later if needed)
- Transaction ID or reference numbers

## Success Metrics

1. 80% of one-time expenses created through dashboard form within 2 weeks of release
2. Average time to create quick payment reduced to under 10 seconds
3. User navigation between dashboard and expense creation reduced by 60%
