# Add Balance Column to Budget Listings PRD

**Ticket**: [Add Balance column to budget listings](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/90)

## Problem Statement
Users currently cannot see their remaining budget balance when viewing the budget list. They must navigate to individual budgets and manually calculate how much budget remains from the initial amount minus expenses. This creates friction in budget management and makes it difficult to quickly assess financial status across multiple budgets.

## Solution Overview
Add a "Balance" column to the budget listings page that displays the current balance (initial budget amount minus total spent amount) for each budget. The balance will show remaining amount as positive values and overspent amounts as negative values, with appropriate visual styling to quickly identify budget status. Success means users can instantly see their budget status without additional navigation or manual calculation.

## User Stories
1. As a budget user, I want to see the current balance for each budget on the listings page, so that I can quickly assess my financial status across all budgets
2. As a budget user, I want to see negative balances clearly highlighted, so that I can immediately identify overspent budgets
3. As a budget user, I want the balance calculation to be accurate and up-to-date, so that I can trust the displayed information for financial decisions

## Acceptance Criteria
- [ ] Budget listings page displays a new "Balance" column showing current balance for each budget
- [ ] Balance calculation shows initial budget amount minus total spent amount from paid expense items
- [ ] Positive balances (remaining budget) are displayed normally
- [ ] Negative balances (overspent) are visually distinguished with appropriate styling
- [ ] Balance values are formatted using the application's currency settings
- [ ] Balance column is properly aligned and responsive across different screen sizes
- [ ] Balance calculation handles edge cases (no expenses, no months) gracefully

## Out of Scope
- Balance calculation caching or performance optimization
- Balance history tracking
- Budget alerts or notifications for overspending
- Balance editing or manual adjustments
- Balance breakdown by category or time period
- Export functionality for balance data

## Success Metrics
1. Balance column appears correctly on budget listings within 1 second load time
2. Balance calculations are accurate for 100% of budgets with expense data
3. Visual distinction between positive and negative balances is clearly visible