# Make Operations Budget-Scoped PRD v1.0

**Last Updated**: 2025-02-06
**Ticket**: [#0044](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/44)

## Problem Statement
Users with multiple budgets cannot work with a specific budget in isolation - all operations show data from all budgets mixed together. This causes confusion when managing separate budgets (e.g., personal vs business) and makes it impossible to focus on one budget at a time. Without budget scoping, users cannot effectively organize their financial data across different contexts.

## Solution Overview
Implement budget-scoped operations by introducing budget-aware URLs and session-based budget selection. Users will select a current budget and all operations (viewing months, creating expenses, dashboard) will be filtered to show only data from that budget. A budget switcher in the UI will allow easy switching between budgets. Success means users can work with one budget at a time without seeing data from other budgets.

## User Stories
1. As a user with multiple budgets, I want to select a current budget, so that I only see and work with data from that specific budget
2. As a user, I want to switch between budgets easily, so that I can manage different financial contexts without confusion
3. As a user, I want all my operations to be budget-aware, so that expenses and months are automatically associated with my current budget
4. As a new user, I want to be prompted to select a budget when I first access the app, so that I have a clear starting context

## Acceptance Criteria
- [ ] User can select a current budget that persists across their session
- [ ] All list views (months, expenses) show only data from the current budget
- [ ] Dashboard displays summary only for the current budget
- [ ] URLs include budget context (e.g., /budgets/1/months/)
- [ ] Budget switcher is accessible from any page
- [ ] Creating new months/expenses respects the current budget context
- [ ] Users without a selected budget are redirected to budget selection

## Out of Scope
- Multi-budget comparison views
- Budget sharing between users
- Budget-level permissions or access control
- Cross-budget transfers or operations
- Budget templates or cloning
- API endpoints for budget operations

## Success Metrics
1. 100% of operations are budget-scoped within 30 days of deployment
2. Zero reported incidents of data mixing between budgets
3. Average budget switching time under 2 seconds
