# Budget Umbrella Entity TRD v1.0

**PRD Reference**: [Budget Umbrella Entity PRD v1.0](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/29)

## Technical Approach

<<<<<<< HEAD
We'll implement the Budget model as a Django entity with a one-to-many relationship to Month model.
The Budget will be added to the existing `expenses` app, maintaining consistency with current
architecture. A Django migration will handle schema changes and data migration to link existing
months to the default budget. The default budget will be seeded via the existing fixture loading
mechanism.
=======
We'll implement the Budget model as a Django entity with a one-to-many relationship to Month model. The Budget will be added to the existing `expenses` app, maintaining consistency with current architecture. A Django migration will handle schema changes and data migration to link existing months to the default budget. The default budget will be seeded via the existing fixture loading mechanism.
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

## Data Model

```python
# New Budget model
class Budget(models.Model):
    name = models.CharField(max_length=255, unique=True)
    start_date = models.DateField()
    initial_amount = models.DecimalField(
        max_digits=13, decimal_places=2, default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Updated Month model
class Month(models.Model):
    # ... existing fields ...
    budget = models.ForeignKey(Budget, on_delete=models.PROTECT)
```

Migration strategy:

1. Create Budget model
2. Create default Budget instance
3. Add budget field to Month as nullable
4. Populate all existing months with default budget
5. Make budget field non-nullable

## API Design

No API changes required - this is a backend-only implementation. Budget calculations will be exposed through model methods:

```python
class Budget:
    def get_total_expenses(self):
        """Calculate total expenses across all linked months"""
        
    def get_balance(self):
        """Return initial_amount minus total expenses"""
```

## Security & Performance

- Delete protection: CASCADE prevention via PROTECT on ForeignKey
- Performance: Database index on Month.budget_id (automatic via ForeignKey)
- Data integrity: Unique constraint on Budget.name
- Migration safety: Multi-step migration to handle existing data

## Technical Risks & Mitigations

1. **Risk**: Existing months without budget assignment → **Mitigation**: Migration creates and assigns default budget
2. **Risk**: Breaking existing Month queries → **Mitigation**: No changes to existing Month fields or ordering
3. **Risk**: Fixture loading order dependencies → **Mitigation**: Add budget to initial_data.json with proper model ordering

## Monitoring & Rollback

- Feature flag: Not required (schema change)
- Key metrics: Migration success, constraint violations
- Rollback: Django migration reversal (`migrate expenses <previous>`)
