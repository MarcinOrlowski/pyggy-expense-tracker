# UI to Manage Budget (Create, Edit, Delete) TRD v1.0

[UI to manage budget (create, edit, delete)](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/41)

**PRD Reference**: 0041_ui_to_manage_budget_PRD.md v1.0

## Technical Approach

We'll implement budget management as a new Django model with CRUD views following the existing
expense tracker patterns. The Budget model will integrate with the existing Month model through a
foreign key relationship. Budget CRUD operations will be implemented using Django's class-based
views with templates following the current Bootstrap/FontAwesome design system. The existing month
processing workflow will be modified to use budget start_date for initial month creation while
maintaining the current sequential month creation pattern.

## Data Model

```python
# New Budget model in expenses/models.py
class Budget(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Modified Month model - add foreign key relationship
class Month(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True, blank=True)
    # ... existing fields remain unchanged

Migration: Add Budget table and budget_id foreign key to Month table
Index: (budget_id, year, month) for efficient budget-month queries
```

## Views & URLs Design

```python
# New views in expenses/views.py
class BudgetListView(ListView)  # GET /budgets/
class BudgetCreateView(CreateView)  # GET/POST /budgets/create/
class BudgetUpdateView(UpdateView)  # GET/POST /budgets/<id>/edit/
class BudgetDeleteView(DeleteView)  # GET/POST /budgets/<id>/delete/

# Modified month processing view
def month_process(request):  # Updated to handle budget integration

# URL patterns in expenses/urls.py
path('budgets/', views.BudgetListView.as_view(), name='budget_list')
path('budgets/create/', views.BudgetCreateView.as_view(), name='budget_create')
path('budgets/<int:pk>/edit/', views.BudgetUpdateView.as_view(), name='budget_edit')
path('budgets/<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete')
```

## Templates Structure

```text
expenses/templates/expenses/
├── budget_list.html          # List all budgets
├── budget_form.html          # Create/Edit budget form
├── budget_confirm_delete.html # Delete confirmation
└── includes/
    └── budget_card.html      # Reusable budget display component
```

## Validation Rules

- Budget name: Required, max 100 characters, unique per user
- Start date: Required, cannot be in the past (except when no months exist)
- Initial amount: Required, decimal field, minimum 0
- Edit start_date: Only allowed when budget has no associated months
- Delete budget: Only allowed when budget has no associated months
- Month creation: Must reference existing budget

## Security & Performance

- Authentication: Use existing Django session authentication
- Authorization: Users can only manage their own budgets (add user foreign key if multi-user)
- Performance: <300ms response time for CRUD operations
- Validation: Server-side validation for all form inputs
- CSRF: Django's built-in CSRF protection for all forms

## Technical Risks & Mitigations

1. **Risk**: Data migration issues with existing Month records → **Mitigation**: Make budget foreign key nullable initially, provide data migration script
2. **Risk**: UI inconsistency with existing design → **Mitigation**: Reuse existing template patterns and CSS classes from expense forms
3. **Risk**: Breaking existing month processing workflow → **Mitigation**: Maintain backward compatibility, add budget integration incrementally

## Implementation Plan

- Phase 1: Budget model + migration + basic CRUD views
- Phase 2: Budget templates following existing UI patterns
- Phase 3: Integration with month processing workflow
- Phase 4: Navigation updates + Default budget handling

Dependencies: None - uses existing Django framework and patterns

## Monitoring & Rollback

- Feature flag: Not required - incremental implementation allows safe rollback
- Key metrics: Budget CRUD operation success rates, month creation with budget association
- Rollback: Remove budget foreign key constraint, revert month processing logic
- Database rollback: Drop Budget table, remove budget_id column from Month table
