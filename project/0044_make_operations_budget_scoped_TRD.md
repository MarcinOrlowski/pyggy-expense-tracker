# Make Operations Budget-Scoped TRD v1.0

**Last Updated**: 2025-02-06
**Ticket**: [#0044](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/44)

## Technical Approach
We'll implement budget scoping using Django's session framework to store the current budget ID, modify URL patterns to include budget_id parameter, and create a middleware/mixin to enforce budget filtering on all relevant queries. A context processor will make the current budget available in all templates, and a budget switcher dropdown in the base template will allow quick budget changes. All views will be updated to filter data based on the session's current budget, with automatic redirection to budget selection for users without a selected budget.

## Data Model
No new models required. Existing relationships:
- Budget → Month (ForeignKey with CASCADE)
- Month → Expense (ForeignKey with CASCADE)
- Expense → ExpenseItem (ForeignKey with CASCADE)

Session storage:
```python
request.session['current_budget_id'] = budget_id
```

## API Design
URL pattern changes:
```
# From:
/expenses/
/months/
/months/<year>/<month>/

# To:
/budgets/<int:budget_id>/expenses/
/budgets/<int:budget_id>/months/
/budgets/<int:budget_id>/months/<year>/<month>/
/budgets/<int:budget_id>/dashboard/

# Budget management (unchanged):
/budgets/
/budgets/create/
/budgets/<int:pk>/edit/
```

Budget selection endpoint:
```
POST /budgets/select/
Request: { budget_id: 1 }
Response: Redirect to /budgets/1/dashboard/
```

## Security & Performance
- Authorization: Users can only access budgets that exist (404 for non-existent)
- Session security: Django's built-in session framework with secure cookies
- Query performance: All queries already filter by relationships, minimal impact
- URL validation: 404 response for invalid budget_id in URLs

## Technical Risks & Mitigations
1. **Risk**: Existing URLs break for users → **Mitigation**: Redirect legacy URLs to current budget equivalent
2. **Risk**: Session expiry loses budget context → **Mitigation**: Redirect to budget selection with friendly message
3. **Risk**: Complex template URL updates → **Mitigation**: Create template tag for budget-aware URL generation

## Implementation Plan
- Phase 1 (S): Create context processor and session management - 2 hours
- Phase 2 (M): Update URL patterns and views to handle budget_id - 4 hours
- Phase 3 (M): Add budget switcher component and template updates - 3 hours
- Phase 4 (S): Update all templates with new URL structure - 2 hours
- Phase 5 (S): Add tests and fix edge cases - 2 hours

Dependencies: None (uses existing Budget model)

## Monitoring & Rollback
- Feature flag: `BUDGET_SCOPING_ENABLED` in settings.py
- Key metrics: Session data for current_budget_id, 404 rates on budget URLs
- Rollback: Set feature flag to False, legacy URLs remain functional

## Implementation Details

### 1. Context Processor (`expenses/context_processors.py`):
```python
def current_budget(request):
    budget_id = request.session.get('current_budget_id')
    budget = None
    if budget_id:
        budget = Budget.objects.filter(id=budget_id).first()
    return {
        'current_budget': budget,
        'current_budget_id': budget_id
    }
```

### 2. View Mixin (`expenses/mixins.py`):
```python
class BudgetScopedMixin:
    def dispatch(self, request, *args, **kwargs):
        budget_id = kwargs.get('budget_id')
        if not Budget.objects.filter(id=budget_id).exists():
            raise Http404
        request.session['current_budget_id'] = budget_id
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        qs = super().get_queryset()
        budget_id = self.kwargs.get('budget_id')
        # Filter based on model type
        return qs.filter(budget_id=budget_id)  # or month__budget_id for expenses
```

### 3. Budget Selection View:
```python
def select_budget(request):
    if request.method == 'POST':
        budget_id = request.POST.get('budget_id')
        if Budget.objects.filter(id=budget_id).exists():
            request.session['current_budget_id'] = budget_id
            return redirect('expenses:dashboard', budget_id=budget_id)
    
    budgets = Budget.objects.all()
    return render(request, 'expenses/budget_select.html', {'budgets': budgets})
```

### 4. Template Updates:
- Replace `{% url 'expenses:month_list' %}` with `{% url 'expenses:month_list' current_budget_id %}`
- Add budget switcher dropdown in base.html header
