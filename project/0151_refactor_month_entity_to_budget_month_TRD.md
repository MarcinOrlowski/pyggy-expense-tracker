# Refactor Month Entity to BudgetMonth TRD

**Ticket**: [Refactor Month entity to BudgetMonth for better semantic clarity](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/151)
**PRD Reference**: 0151_refactor_month_entity_to_budget_month_PRD.md

## Technical Approach

This refactoring will rename the Month model to BudgetMonth throughout the Django
application using a systematic find-and-replace approach. The implementation will update
all Python code references, create a database migration to rename the table from
`expenses_month` to `expenses_budgetmonth`, and update Django admin, forms, views, and
templates. Since this is purely a naming refactoring, no business logic changes are
required.

## Data Model

The existing Month model will be renamed to BudgetMonth with identical fields and relationships:

```python
# Before: expenses/models/month.py -> Month
# After: expenses/models/month.py -> BudgetMonth

class BudgetMonth(models.Model):
    budget = models.ForeignKey("Budget", on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(...)
    month = models.PositiveSmallIntegerField(...)
    # ... other fields remain identical

    class Meta:
        db_table = "expenses_budgetmonth"  # Django migration will handle rename
        unique_together = ["budget", "year", "month"]
        ordering = ["-year", "-month"]
```

**Database Changes:**

- Table rename: `expenses_month` → `expenses_budgetmonth`
- Foreign key references from other tables will be automatically handled by Django
- All indexes and constraints remain functionally identical

## API Design

No API endpoint changes are required since this is a model-level refactoring. All existing URL patterns and view responses remain identical:

```python
# URLs remain unchanged:
# /months/ -> still lists budget months
# /months/create/ -> still creates budget months
# /months/{id}/ -> still shows budget month details

# Django admin URLs automatically adapt to new model name:
# /admin/expenses/month/ -> /admin/expenses/budgetmonth/
```

## Security & Performance

- **Performance**: No performance impact - identical database operations with renamed table
- **Security**: No security implications - same access patterns and permissions
- **Data integrity**: Django migration ensures referential integrity during table rename
- **Downtime**: Migration requires brief table lock (~1-2 seconds for typical dataset)

## Technical Risks & Mitigations

1. **Risk**: Migration failure on large datasets → **Mitigation**: Test migration on database backup first, include rollback migration
2. **Risk**: Missed references causing runtime errors → **Mitigation**: Comprehensive grep search and systematic file-by-file verification
3. **Risk**: Template rendering errors → **Mitigation**: Test all Month-related templates in development environment

## Implementation Plan

- **Phase 1** (S): Update model file and create migration - 1 hour
  - Rename Month class to BudgetMonth in `expenses/models/month.py`
  - Create Django migration for table rename
  - Update `expenses/models/__init__.py` imports

- **Phase 2** (M): Update Python references - 2 hours
  - Update all imports in views, forms, services, admin
  - Update all model relationships in other models
  - Update all test files

- **Phase 3** (S): Update templates and run tests - 1 hour
  - Update template references to model
  - Run full test suite to verify functionality
  - Fix any remaining issues

**Dependencies**: None - this is an isolated refactoring

## Monitoring & Rollback

- **Feature flag**: Not applicable - this is a model refactoring
- **Key metrics**: Monitor for any 500 errors post-deployment, verify all Month-related pages load
- **Rollback**:
  1. Reverse migration: `python manage.py migrate expenses <previous_migration>`
  2. Git revert: `git revert <commit_hash>`
  3. Redeploy previous version if necessary

## Migration Strategy

```python
# Migration file will include:
operations = [
    migrations.RenameModel(
        old_name='Month',
        new_name='BudgetMonth',
    ),
]
```

**Testing approach:**

1. Create database backup before migration
2. Test migration on copy of production data
3. Verify all existing functionality after migration
4. Run complete test suite to ensure no regressions
