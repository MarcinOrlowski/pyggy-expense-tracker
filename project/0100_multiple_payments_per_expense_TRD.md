# Multiple Payments per Expense TRD

**Ticket**: [Rework payments to allow multiple payments per expense](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/100)
**PRD Reference**: 0100_multiple_payments_per_expense_PRD.md

## Technical Approach

Currently, ExpenseItem stores payment data directly on the model (payment_date, payment_method,
payment_id, status) allowing only one payment per expense item. We'll create a new Payment model
with a many-to-one relationship to ExpenseItem, enabling multiple payments per item. ExpenseItem
will be refactored to calculate payment status dynamically from the sum of associated Payment
amounts. The existing payment form workflow currently updates ExpenseItem fields directly and will
be modified to create Payment entries while preserving the same user interface and validation to
prevent overpayments.

## Data Model

New Payment model:

```python
class Payment(models.Model):
    expense_item = models.ForeignKey(ExpenseItem, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=13, decimal_places=2, validators=[MinValueValidator(0.01)])
    payment_date = models.DateTimeField()
    payment_method = models.ForeignKey(PaymentMethod, null=True, blank=True, on_delete=models.SET_NULL)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Updated ExpenseItem methods:

```python
def get_total_paid(self):
    return self.payment_set.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

def get_remaining_amount(self):
    return self.amount - self.get_total_paid()

@property
def status(self):
    return self.STATUS_PAID if self.get_total_paid() >= self.amount else self.STATUS_PENDING
```

## API Design

No new API endpoints required. Existing payment form POST endpoint will be modified:

```text
POST /budget/{budget_id}/expense-item/{pk}/pay/
Request: { payment_date: "2024-01-15T10:30", amount: "25.50", payment_method: 1 }
Response: Redirect to dashboard with success message

Validation: amount <= expense_item.get_remaining_amount()
Error: ValidationError if amount exceeds remaining balance
```

## Security & Performance

- Authentication: Existing budget-scoped access control maintained
- Validation: Payment amount must be > 0 and <= remaining balance  
- Performance: Payment queries will use expense_item foreign key index
- Data integrity: CASCADE delete ensures Payment cleanup when ExpenseItem deleted

## Technical Risks & Mitigations

1. **Risk**: Migration complexity with existing payment data → **Mitigation**: Two-step migration
   preserving ExpenseItem payment fields temporarily
1. **Risk**: Decimal precision issues in payment calculations → **Mitigation**: Use Decimal type
   throughout, avoid float arithmetic
1. **Risk**: Performance impact from payment aggregation queries → **Mitigation**: Database-level
   SUM aggregation, add index on expense_item_id

## Implementation Plan

- Phase 1 (M): Create Payment model and migration - 3 days
- Phase 2 (M): Refactor ExpenseItem payment methods and status calculation - 2 days  
- Phase 3 (M): Update PaymentForm and payment views to use Payment - 2 days
- Phase 4 (S): Update templates to display payment history and totals - 2 days
- Phase 5 (S): Data migration from existing ExpenseItem payments - 1 day
- Phase 6 (S): Update services.py expense completion logic - 1 day

Dependencies: None

## Monitoring & Rollback

- Feature flag: Not required (data migration approach allows rollback)
- Key metrics: Payment creation success rate, validation error frequency
- Rollback: Revert migration and restore ExpenseItem payment fields from backup
- Testing: Validate payment totals match expected amounts, ensure no overpayments possible
