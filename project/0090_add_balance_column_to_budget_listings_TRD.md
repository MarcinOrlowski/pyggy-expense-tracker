# Add Balance Column to Budget Listings TRD

**Ticket**: [Add Balance column to budget listings](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/90)
**PRD Reference**: 0090_add_balance_column_to_budget_listings_PRD.md

## Technical Approach

We'll implement balance calculation by adding a `get_current_balance()` method to the Budget model
that calculates the difference between initial_amount and total paid expenses. The budget_list view
will be modified to include balance data, and the budget_list.html template will be updated to
display the new Balance column. This approach uses on-the-fly calculation for accuracy and
simplicity, avoiding caching complexity in the initial implementation.

## Data Model

No new database tables or schema changes required. Existing models used:

- `Budget.initial_amount` - starting budget amount
- `ExpenseItem` - individual expense records with amount and status fields
- Calculation: `Budget.initial_amount - sum(ExpenseItem.amount WHERE status='paid' AND expense.budget=budget)`

## API Design

No new API endpoints required. Modification to existing view:

```python
# expenses/views.py - budget_list function
def budget_list(request):
    budgets = Budget.objects.all()
    # Add balance calculation for each budget
    for budget in budgets:
        budget.current_balance = budget.get_current_balance()
    context = {'budgets': budgets}
    return render(request, 'expenses/budget_list.html', context)
```

## Security & Performance

- Performance: Balance calculation involves one database query per budget (N+1 could be optimized
  with select_related/prefetch_related if needed)
- Target: <500ms page load time for up to 50 budgets
- Security: No additional security considerations - uses existing model access patterns

## Technical Risks & Mitigations

1. **Risk**: N+1 query problem with multiple budgets → **Mitigation**: Monitor performance, add
   query optimization if needed in future iterations
1. **Risk**: Calculation inconsistency with stale data → **Mitigation**: Real-time calculation
   ensures accuracy, no caching to maintain
1. **Risk**: Large expense datasets causing slow queries → **Mitigation**: Database indexes on
   expense.budget_id and expenseitem.status fields

## Implementation Plan

- Phase 1 (S): Add `get_current_balance()` method to Budget model - 30 minutes
- Phase 2 (S): Modify budget_list view to include balance calculations - 15 minutes  
- Phase 3 (S): Update budget_list.html template with Balance column - 30 minutes
- Phase 4 (S): Add CSS styling for negative balances - 15 minutes
- Phase 5 (XS): Testing and edge case handling - 30 minutes

Total estimate: 2 hours

Dependencies: None

## Monitoring & Rollback

- Feature flag: Not required for this UI enhancement
- Key metrics: Page load time for budget list, accuracy of balance calculations
- Rollback: Remove Balance column from template, revert view changes - template change can be quickly reverted if issues arise
