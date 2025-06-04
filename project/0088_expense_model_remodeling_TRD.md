# Expense Model Remodeling TRD

**Ticket**: [Rework expense and expense item due date functionality](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/89)
**PRD Reference**: User request to restructure expense model for better due date handling

## Technical Approach

We'll restructure the Expense model to separate schedule definition from actual occurrences. The Expense will define the payment pattern (when, how much, how often), while ExpenseItem represents individual payment instances with their own due dates. This eliminates the need for due_date on Expense and creates a cleaner separation of concerns. The refactoring will use Django data migrations to preserve existing data integrity.

**Documentation Standards**: All field meanings, validation logic, and business rules will be thoroughly documented in code comments and docstrings to ensure maintainability and clarity for future developers.

## Data Model

### Updated Expense Model
```python
class Expense(models.Model):
    """
    Expense schedule definition - defines WHEN and HOW MUCH to pay.
    Individual payment instances are represented by ExpenseItem objects.
    
    Field Usage by Expense Type:
    - ONE_TIME: amount=total cost, day_of_month from start_date
    - ENDLESS_RECURRING: amount=monthly cost, day_of_month for scheduling  
    - RECURRING_WITH_END: amount=monthly cost, day_of_month + end_date
    - SPLIT_PAYMENT: amount=per-installment, total_parts + skip_parts
    """
    
    # Core scheduling fields
    start_date = models.DateField(
        help_text="When this expense schedule begins (renamed from started_at)"
    )
    amount = models.DecimalField(
        help_text="Per-installment amount for split payments, total amount for others"
    )
    day_of_month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Day of month when payment is due (fallback logic for shorter months)"
    )
    
    # Split payment specific fields  
    total_parts = models.PositiveIntegerField(
        default=0,
        help_text="Total number of installments for split payments (renamed from installments_count)"
    )
    skip_parts = models.PositiveIntegerField(
        default=0, 
        help_text="Number of initial parts to skip - for tracking remaining payments (renamed from initial_installment)"
    )
    
    # Unchanged fields: budget, payee, title, expense_type, end_date, closed_at, notes, created_at, updated_at
```

### Field Usage by Type
- **One-time**: `amount` = total cost, `day_of_month` from start_date
- **Endless recurring**: `amount` = monthly cost, `day_of_month` for scheduling
- **Recurring with end**: `amount` = monthly cost, `day_of_month` + `end_date`
- **Split payment**: `amount` = per-installment, `total_parts` + `skip_parts`

### Day-of-Month Fallback Logic
```python
def get_due_date_for_month(self, year, month):
    """
    Calculate actual due date for a given month, handling months with fewer days.
    
    Examples:
    - day_of_month=15: Always returns 15th (all months have 15+ days)
    - day_of_month=30 in February: Returns 28th/29th (Feb's last day)
    - day_of_month=31 in April: Returns 30th (April's last day)
    
    Logic: Use min(requested_day, last_day_of_month)
    """
    last_day_of_month = calendar.monthrange(year, month)[1]
    actual_day = min(self.day_of_month, last_day_of_month)
    return date(year, month, actual_day)
```

## API Design

No new API endpoints needed. Existing form handling will be updated:

```python
class ExpenseForm(forms.ModelForm):
    def clean(self):
        """
        Enhanced validation with detailed business rule documentation:
        
        1. day_of_month validation (1-31 range)
        2. Auto-populate day_of_month from start_date.day if not provided
        3. Type-specific validation:
           - SPLIT_PAYMENT: total_parts > 0, skip_parts < total_parts
           - RECURRING_WITH_END: end_date required and >= start_date
           - Others: total_parts=0, skip_parts=0
        """
        
class Expense(models.Model):
    def get_due_date_for_month(self, year, month):
        """Calculate actual due date with day-of-month fallback logic"""
        
    def calculate_total_cost(self):
        """
        Calculate total cost based on expense type:
        - SPLIT_PAYMENT: amount × total_parts
        - Others: amount (already the total)
        """
        
    def get_remaining_parts(self):
        """
        For split payments: total_parts - skip_parts
        Used to determine how many payments are still pending
        """
```

## Security & Performance

- **Data integrity**: Multi-step migration ensures no data loss during restructuring
- **Validation**: Enhanced form validation prevents invalid day_of_month values
- **Performance**: No additional database queries - existing relationships maintained
- **Backward compatibility**: Existing ExpenseItem.due_date logic unchanged

## Technical Risks & Mitigations

1. **Risk**: Data loss during field renaming migration → **Mitigation**: Multi-step migration with data preservation checks
2. **Risk**: Invalid day_of_month causing calculation errors → **Mitigation**: Robust fallback logic + validation constraints
3. **Risk**: Form validation complexity increases → **Mitigation**: Comprehensive test coverage for all expense types

## Implementation Plan

- **Phase 1** (M): Create data migration removing due_date field - 1 day
- **Phase 2** (L): Update Expense model with new field structure - 2 days  
- **Phase 3** (L): Update ExpenseForm and validation logic - 2 days
- **Phase 4** (M): Update templates and JavaScript for new fields - 1 day
- **Phase 5** (S): Update tests and documentation - 1 day

Dependencies: None

## Monitoring & Rollback

- **Feature flag**: Not needed - database schema change
- **Key metrics**: Monitor form submission success rate during rollout
- **Rollback**: Reverse migrations available for each phase
- **Validation**: Pre-migration data export + post-migration integrity checks

## Migration Strategy

1. Remove due_date field from Expense (reverse previous migration)
2. Rename started_at → start_date  
3. Add day_of_month field, populate from start_date.day
4. Rename installments_count → total_parts
5. Rename initial_installment → skip_parts
6. Update validation constraints and help text