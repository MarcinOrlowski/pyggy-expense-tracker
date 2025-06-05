# Global Payment Methods Management TRD

**Ticket**: [Implement global payment methods management](https://github.com/MarcinOrlowski/python-expense-tracker/issues/99)
**PRD Reference**: 0099_implement_global_payment_methods_management_PRD.md

## Technical Approach
We'll implement standard Django class-based views (CreateView, UpdateView, DeleteView) for payment method CRUD operations, following the existing pattern used for other entities like Payee. The PaymentMethod model remains unchanged as it's already global. We'll add protection against deleting payment methods that are referenced by ExpenseItem records. All views will integrate with the existing template structure and maintain consistent styling.

## Data Model
No changes required - existing PaymentMethod model is sufficient:
```python
PaymentMethod
- id (PK)
- name (CharField, max_length=100)
- created_at (DateTimeField)
- updated_at (DateTimeField)

ExpenseItem.payment_method (FK -> PaymentMethod, nullable)
```

## API Design
URL patterns following existing conventions:
```
GET    /payment-methods/                 # List all (existing)
GET    /payment-methods/create/          # Create form
POST   /payment-methods/create/          # Create submission
GET    /payment-methods/<id>/edit/       # Edit form
POST   /payment-methods/<id>/edit/       # Edit submission  
GET    /payment-methods/<id>/delete/     # Delete confirmation
POST   /payment-methods/<id>/delete/     # Delete submission
```

Forms:
- PaymentMethodForm with single 'name' field
- Standard Django validation

## Security & Performance
- Authentication: Uses existing @login_required decorator
- Authorization: All authenticated users can manage payment methods
- Validation: Prevent deletion of payment methods in use
- Performance: Simple queries with no N+1 issues

## Technical Risks & Mitigations
1. **Risk**: Deleting payment method breaks expense history → **Mitigation**: Check ExpenseItem references before deletion
2. **Risk**: Concurrent editing conflicts → **Mitigation**: Use Django's built-in optimistic locking with updated_at field

## Implementation Plan
- Phase 1 (S): Create forms.py entries for PaymentMethodForm - 15 min
- Phase 2 (M): Implement CRUD views in views.py - 45 min
- Phase 3 (M): Create templates (create, edit, delete confirmation) - 45 min
- Phase 4 (S): Update URLs and navigation links - 20 min
- Phase 5 (S): Test all operations - 30 min

Dependencies: None

## Monitoring & Rollback
- Feature flag: None needed (low-risk feature)
- Key metrics: Track 500 errors on payment method endpoints
- Rollback: Remove navigation links to disable UI access; Django admin remains available