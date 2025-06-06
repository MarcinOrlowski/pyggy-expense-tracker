# Make Operations Budget-Scoped TRD v1.0

**Last Updated**: 2025-02-06
**Ticket**: [#0044](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/44)

## Technical Approach

We'll implement budget scoping by modifying URL patterns to include budget_id parameter and updating
all views to filter data based on the budget from the URL. A context processor will make the current
budget available in all templates by extracting it from the URL parameters. The current budget will
be displayed in the header with a link to switch budgets. All views will be updated to filter data
based on the budget_id from the URL, with automatic redirection to budget selection for users
accessing the root URL.

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

```text
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

```text
POST /budgets/select/
Request: { budget_id: 1 }
Response: Redirect to /budgets/1/dashboard/
```

## Security & Performance

- Authorization: Users can only access budgets that exist (404 for non-existent)
- Session security: Django's built-in session framework with secure cookies (no need - not using auth)
- Query performance: All queries already filter by relationships, minimal impact
- URL validation: 404 response for invalid budget_id in URLs

## Technical Risks & Mitigations

1. **Risk**: Existing URLs break for users → **Mitigation**: No need. That's project under development.
2. **Risk**: Session expiry loses budget context → **Mitigation**: why session keeps budget context? it's always referenced in URL?
3. **Risk**: Complex template URL updates → **Mitigation**: Create template tag for budget-aware URL generation

## Implementation Plan

- Phase 1 (S): Create context processor and session management
- Phase 2 (M): Update URL patterns and views to handle budget_id
- Phase 3 (M): Add current budget display and template updates
- Phase 4 (S): Update all templates with new URL structure
- Phase 5 (S): Add tests and fix edge cases

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
